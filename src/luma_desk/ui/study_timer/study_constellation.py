import json
import calendar
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame


class StudyConstellation(QFrame):

    # Grid geometry. Weeks run left to right along a row, and each
    # row underneath is the next week - a normal month calendar,
    # rather than a GitHub-style column-per-week heatmap.
    CELL_SIZE = 20
    GAP = 4
    COLUMNS = 7  # Sunday through Saturday
    MAX_ROWS = 6  # A month can span at most 6 calendar weeks

    def __init__(self):
        super().__init__()

        # Data
        project_root = Path(__file__).resolve().parents[4]
        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "study.json"
        self.data_folder.mkdir(exist_ok=True)
        self.data = self.load_data()

        # Current month
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        # Widget
        self.setMinimumSize(340, 250)
        self.setMouseTracking(True)
        self.hovered_date = None

        # Styling
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 190);
                border-radius: 12px;
            }
        """)

    # Data
    def load_data(self):
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def refresh(self):
        self.data = self.load_data()
        self.update()

    # Month information
    def month_name(self):
        return calendar.month_name[self.current_month]

    def days_in_month(self):
        return calendar.monthrange(self.current_year, self.current_month)[1]

    def first_weekday(self):
        weekday = calendar.monthrange(self.current_year, self.current_month)[0]
        return (weekday + 1) % 7

    # Study months
    def get_study_months(self):
        months = set()

        for date_string, seconds in self.data.items():
            if not seconds:
                continue

            try:
                day = date.fromisoformat(date_string)
                months.add((day.year, day.month))
            except ValueError:
                continue

        today = date.today()
        months.add((today.year, today.month))
        return sorted(months)

    # Navigation
    def can_go_previous(self):
        months = self.get_study_months()
        current = (self.current_year, self.current_month)
        return months.index(current) > 0

    def can_go_next(self):
        months = self.get_study_months()
        current = (self.current_year, self.current_month)
        return months.index(current) < len(months) - 1

    def previous_month(self):
        if not self.can_go_previous():
            return

        months = self.get_study_months()
        current = (self.current_year, self.current_month)
        current_index = months.index(current)
        self.current_year, self.current_month = months[current_index - 1]
        self.hovered_date = None
        self.setToolTip("")
        self.update()

    def next_month(self):
        if not self.can_go_next():
            return

        months = self.get_study_months()
        current = (self.current_year, self.current_month)
        current_index = months.index(current)
        self.current_year, self.current_month = months[current_index + 1]
        self.hovered_date = None
        self.setToolTip("")
        self.update()

    # Study information
    def get_seconds(self, day):
        return self.data.get(day.isoformat(), 0)

    def get_study_days(self):
        count = 0

        for day_number in range(1, self.days_in_month() + 1):
            day = date(self.current_year, self.current_month, day_number)

            if self.get_seconds(day) > 0:
                count += 1

        return count

    def get_month_total(self):
        total = 0

        for day_number in range(1, self.days_in_month() + 1):
            day = date(self.current_year, self.current_month, day_number)
            total += self.get_seconds(day)

        return total

    def get_current_streak(self):
        """How many days in a row have been studied, up to today."""

        day = date.today()

        # Today isn't over yet, so an empty today doesn't break a streak.
        if self.get_seconds(day) <= 0:
            day = day - timedelta(days=1)

        streak = 0

        while self.get_seconds(day) > 0:
            streak += 1
            day = day - timedelta(days=1)

        return streak

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"

        return f"{minutes}m" if minutes > 0 else "0m"

    def summary_text(self):
        study_days = self.get_study_days()
        day_text = "day" if study_days == 1 else "days"

        parts = [
            f"{study_days} study {day_text}",
            self.format_time(self.get_month_total()),
        ]

        streak = self.get_current_streak()

        if streak > 0:
            parts.append(f"✦ {streak} day streak")

        return "  ·  ".join(parts)

    # Cell colour
    def get_cell_color(self, seconds):
        if seconds <= 0:
            return QColor(255, 244, 220, 18)

        if seconds < 1 * 60 * 60:
            return QColor(232, 213, 177, 100)

        if seconds < 2 * 60 * 60:
            return QColor(232, 213, 177, 145)

        if seconds < 3 * 60 * 60:
            return QColor(232, 213, 177, 195)

        return QColor(232, 213, 177, 240)

    # Grid geometry shared by painting and mouse handling
    def grid_origin(self):
        grid_width = self.COLUMNS * self.CELL_SIZE + (self.COLUMNS - 1) * self.GAP

        grid_x = (self.width() - grid_width) / 2
        grid_y = 76  # Leaves room for the title, summary, and weekday header

        return grid_x, grid_y

    def cell_rect(self, day_number, grid_x, grid_y):
        index = self.first_weekday() + day_number - 1

        week_row = index // 7
        weekday_column = index % 7

        x = grid_x + weekday_column * (self.CELL_SIZE + self.GAP)
        y = grid_y + week_row * (self.CELL_SIZE + self.GAP)

        return QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)

    # Painting
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Title
        title_font = QFont("Lora", 14)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(QRectF(45, 12, self.width() - 90, 25), Qt.AlignmentFlag.AlignCenter, f"{self.month_name()} {self.current_year}")

        # Study summary
        summary_font = QFont("Lora", 9)
        painter.setFont(summary_font)
        painter.setPen(QColor(255, 255, 255, 170))
        painter.drawText(QRectF(20, 36, self.width() - 40, 18), Qt.AlignmentFlag.AlignCenter, self.summary_text())

        # Navigation arrows
        arrow_font = QFont("Lora", 17)
        arrow_font.setBold(True)
        painter.setFont(arrow_font)

        previous_alpha = 190 if self.can_go_previous() else 55
        painter.setPen(QColor(255, 255, 255, previous_alpha))
        painter.drawText(QRectF(10, 12, 30, 25), Qt.AlignmentFlag.AlignCenter, "‹")

        next_alpha = 190 if self.can_go_next() else 55
        painter.setPen(QColor(255, 255, 255, next_alpha))
        painter.drawText(QRectF(self.width() - 40, 12, 30, 25), Qt.AlignmentFlag.AlignCenter, "›")

        # Grid geometry
        grid_x, grid_y = self.grid_origin()

        # Weekday header, running along the top
        weekday_font = QFont("Lora", 8)
        painter.setFont(weekday_font)
        weekday_names = ["S", "M", "T", "W", "T", "F", "S"]
        painter.setPen(QColor(255, 255, 255, 145))

        for column in range(self.COLUMNS):
            x = grid_x + column * (self.CELL_SIZE + self.GAP)

            painter.drawText(
                QRectF(x, grid_y - 20, self.CELL_SIZE, 16),
                Qt.AlignmentFlag.AlignCenter,
                weekday_names[column],
            )

        # Calendar cells, one row per week
        days = self.days_in_month()
        today = date.today()

        for day_number in range(1, days + 1):
            current_day = date(self.current_year, self.current_month, day_number)
            seconds = self.get_seconds(current_day)
            cell_rect = self.cell_rect(day_number, grid_x, grid_y)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.get_cell_color(seconds)))
            painter.drawRoundedRect(cell_rect, 5, 5)

            # Mark today so it's easy to find
            if current_day == today:
                painter.setPen(QPen(QColor(255, 255, 255, 130), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(cell_rect.adjusted(-2, -2, 2, 2), 6, 6)

            if self.hovered_date == current_day:
                painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(cell_rect, 5, 5)

        # Legend, reserving space for the full six rows so it lands
        # in the same place regardless of how many weeks this month uses.
        grid_height = self.MAX_ROWS * self.CELL_SIZE + (self.MAX_ROWS - 1) * self.GAP
        legend_y = grid_y + grid_height + 6

        legend_font = QFont("Lora", 8)
        painter.setFont(legend_font)
        painter.setPen(QColor(255, 255, 255, 135))
        painter.drawText(QRectF(grid_x - 5, legend_y, 35, 16), Qt.AlignmentFlag.AlignLeft, "Less")

        legend_values = [0, 30 * 60, 60 * 60, 2 * 60 * 60, 3 * 60 * 60]
        legend_x = grid_x + 33

        for seconds in legend_values:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.get_cell_color(seconds)))
            painter.drawRoundedRect(QRectF(legend_x, legend_y + 1, 14, 14), 4, 4)
            legend_x += 19

        painter.setPen(QColor(255, 255, 255, 135))
        painter.drawText(QRectF(legend_x + 2, legend_y, 40, 16), Qt.AlignmentFlag.AlignLeft, "More")

    # Mouse hover
    def mouseMoveEvent(self, event):
        mouse_x = event.position().x()
        mouse_y = event.position().y()

        if 10 <= mouse_x <= 40 and 10 <= mouse_y <= 42 and self.can_go_previous():
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif self.width() - 40 <= mouse_x <= self.width() - 10 and 10 <= mouse_y <= 42 and self.can_go_next():
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        grid_x, grid_y = self.grid_origin()
        days = self.days_in_month()

        self.hovered_date = None

        for day_number in range(1, days + 1):
            rect = self.cell_rect(day_number, grid_x, grid_y)

            if rect.contains(mouse_x, mouse_y):
                current_day = date(self.current_year, self.current_month, day_number)
                self.hovered_date = current_day
                self.show_day_tooltip(current_day, self.get_seconds(current_day))
                break

        if self.hovered_date is None:
            self.setToolTip("")

        self.update()

    # Mouse click
    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.position().x()
        y = event.position().y()

        if 10 <= x <= 40 and 10 <= y <= 42 and self.can_go_previous():
            self.previous_month()
            return

        if self.width() - 40 <= x <= self.width() - 10 and 10 <= y <= 42 and self.can_go_next():
            self.next_month()
            return

    # Tooltip
    def show_day_tooltip(self, day, seconds):
        time_text = self.format_time(seconds)

        if seconds > 0:
            text = f"{day.strftime('%A, %B %d, %Y')}\nStudied: {time_text}"
        else:
            text = f"{day.strftime('%A, %B %d, %Y')}\nNo study time"

        self.setToolTip(text)

    # Mouse leave
    def leaveEvent(self, event):
        self.hovered_date = None
        self.setToolTip("")
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()