import json
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from luma_desk.ui.planner.deadline_row import DeadlineRow


class PlannerState:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "planner.json"

        self.data_folder.mkdir(exist_ok=True)

        self.states = self.load()

    def load(self):
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(self.states, file, indent=4)
        except OSError as error:
            print("Could not save planner data:", error)

    def get_deadlines(self):
        deadlines = self.states.get("deadlines", [])

        cleaned = []

        for deadline in deadlines:
            try:
                due = date.fromisoformat(deadline["due"])
            except (KeyError, TypeError, ValueError):
                continue

            cleaned.append({
                "title": deadline.get("title", ""),
                "due": due,
                "done": bool(deadline.get("done", False)),
            })

        return cleaned

    def set_deadlines(self, deadlines):
        self.states["deadlines"] = [
            {
                "title": deadline["title"],
                "due": deadline["due"].isoformat(),
                "done": deadline["done"],
            }
            for deadline in deadlines
        ]

        self.save()


class Planner(QFrame):
    def __init__(self):
        super().__init__()

        self.state = PlannerState()
        self.rows = []

        # Widget styling
        self.setFixedWidth(260)
        self.setMinimumHeight(340)

        self.setStyleSheet("""
            QFrame#planner {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 70);
                border-radius: 3px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 12px;
                padding: 7px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }
        """)

        self.setObjectName("planner")

        # Title
        self.title = QLabel("✿ Planner")
        self.title.setAlignment(Qt.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
            }
        """)

        # Empty message
        self.empty_label = QLabel("Nothing due yet.")
        self.empty_label.setAlignment(Qt.AlignCenter)

        self.empty_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 140);
                font-family: "Nunito Sans";
                font-size: 11px;
            }
        """)

        # Scrolling list of deadlines
        self.row_layout = QVBoxLayout()
        self.row_layout.setSpacing(2)
        self.row_layout.setContentsMargins(0, 0, 6, 0)
        self.row_layout.addWidget(self.empty_label)
        self.row_layout.addStretch()

        self.row_container = QWidget()
        self.row_container.setStyleSheet("background: transparent;")
        self.row_container.setLayout(self.row_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.row_container)

        # Add button
        self.add_button = QPushButton("+ Add deadline")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_deadline)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 18, 15, 12)
        layout.setSpacing(10)

        layout.addWidget(self.title)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        # Re-sorting rebuilds every row, so it waits until the
        # student has stopped fiddling with the date.
        self.sort_timer = QTimer(self)
        self.sort_timer.setInterval(1500)
        self.sort_timer.setSingleShot(True)
        self.sort_timer.timeout.connect(self.sort_rows)

        # The app might be left open overnight, so the countdowns
        # are refreshed every so often.
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(10 * 60 * 1000)
        self.refresh_timer.timeout.connect(self.refresh_countdowns)
        self.refresh_timer.start()

        self.build_rows(self.state.get_deadlines())

    # Rows
    def build_rows(self, deadlines):
        for row in self.rows:
            self.row_layout.removeWidget(row)
            row.deleteLater()

        self.rows = []

        # Unfinished work first, then soonest due date.
        deadlines = sorted(
            deadlines,
            key=lambda deadline: (deadline["done"], deadline["due"])
        )

        for position, deadline in enumerate(deadlines):
            row = DeadlineRow(
                deadline["title"],
                deadline["due"],
                deadline["done"],
            )

            row.changed.connect(self.save_rows)
            row.reordered.connect(self.row_reordered)

            row.deleted.connect(
                lambda row=row: self.delete_row(row)
            )

            self.row_layout.insertWidget(position, row)
            self.rows.append(row)

        self.empty_label.setVisible(not self.rows)

    def collect_rows(self):
        return [
            {
                "title": row.get_title(),
                "due": row.get_due(),
                "done": row.done,
            }
            for row in self.rows
        ]

    def save_rows(self):
        self.state.set_deadlines(self.collect_rows())

    def row_reordered(self):
        self.save_rows()
        self.sort_timer.start()

    def sort_rows(self):
        self.build_rows(self.collect_rows())

    def refresh_countdowns(self):
        for row in self.rows:
            row.update_appearance()

    def add_deadline(self):
        deadlines = self.collect_rows()

        deadlines.append({
            "title": "",
            "due": date.today() + timedelta(days=7),
            "done": False,
        })

        self.state.set_deadlines(deadlines)
        self.build_rows(deadlines)

        # Let the student type straight away.
        for row in self.rows:
            if not row.get_title():
                row.title.setFocus()
                break

    def delete_row(self, row):
        if row not in self.rows:
            return

        self.rows.remove(row)

        self.row_layout.removeWidget(row)
        row.deleteLater()

        self.save_rows()

        self.empty_label.setVisible(not self.rows)

    # Used by the dashboard header
    def next_deadline(self):
        upcoming = [row for row in self.rows if not row.done]

        if not upcoming:
            return None

        return min(upcoming, key=lambda row: row.get_due())