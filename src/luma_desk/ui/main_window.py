from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from luma_desk.ui.header import Header
from luma_desk.ui.dashboard import Dashboard
from luma_desk.ui.todo.to_do import ToDo
from luma_desk.ui.planner.planner_widget import Planner
from luma_desk.ui.spotify.spotify_widget import SpotifyWidget
from luma_desk.ui.pomodoro.pomodoro_widget import PomodoroWidget
from luma_desk.ui.calculator.calculator_widget import CalculatorWidget
from luma_desk.ui.links.links_widget import QuickLinks
from luma_desk.ui.notes.notes_widget import Notes
from luma_desk.ui.quotes.quotes_widget import QuoteCard
from luma_desk.ui.study_timer.study_timer import StudyTimer
from luma_desk.ui.study_timer.study_constellation import StudyConstellation


class BackgroundWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Load background image
        project_root = Path(__file__).resolve().parents[3]
        background_path = project_root / "assets" / "background.png"

        self.background = QPixmap(str(background_path))

        # Header
        self.header = Header()

        # Dashboard
        self.dashboard = Dashboard()

        self.header.tidy_requested.connect(self.dashboard.tidy)

        # To Do
        self.to_do = ToDo()
        self.dashboard.add_card("todo", "To Do", self.to_do, 40, 40)

        # Planner
        self.planner = Planner()
        self.dashboard.add_card("planner", "Planner", self.planner, 280, 40)

        # Pomodoro
        self.pomodoro = PomodoroWidget()
        self.dashboard.add_card("pomodoro", "Pomodoro", self.pomodoro, 560, 40)

        # Spotify
        self.spotify = SpotifyWidget()
        self.dashboard.add_card("spotify", "Spotify", self.spotify, 800, 40)

        # Study Constellation
        self.study_constellation = StudyConstellation()
        self.dashboard.add_card("study_constellation", "Study", self.study_constellation, 1070, 40)

        # Calculator
        self.calculator = CalculatorWidget()
        self.dashboard.add_card("calculator", "Calculator", self.calculator, 40, 480)

        # Scratchpad
        self.notes = Notes()
        self.dashboard.add_card("notes", "Notes", self.notes, 300, 480)

        # Quick links
        self.quick_links = QuickLinks()
        self.dashboard.add_card("links", "Links", self.quick_links, 580, 480)

        # Quote of the day
        self.quote = QuoteCard()
        self.dashboard.add_card("quote", "Quote", self.quote, 800, 480)

        # Floating study timer
        self.study_timer = StudyTimer()

        self.study_timer.setParent(self)

        self.study_timer.adjustSize()

        self.study_timer.show()

        self.study_timer.raise_()

        self.study_timer.study_updated.connect(self.study_constellation.refresh)
        self.study_timer.study_updated.connect(self.update_study_total)

        # Finished pomodoro sessions count towards today's study time.
        self.pomodoro.focus_completed.connect(self.study_timer.add_seconds)

        # Main layout
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.header)
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

        self.position_study_timer()
        self.study_timer.raise_()

        # Keep the header total moving while the timer runs.
        self.update_study_total()

        self.header_timer = QTimer(self)
        self.header_timer.setInterval(30 * 1000)
        self.header_timer.timeout.connect(self.update_study_total)
        self.header_timer.start()

    def update_study_total(self):
        self.header.set_study_seconds(self.study_timer.get_today_seconds())

    def position_study_timer(self):
        margin = 20

        x = (
            self.width()
            - self.study_timer.width()
            - margin
        )

        y = (
            self.height()
            - self.study_timer.height()
            - margin
        )

        self.study_timer.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.position_study_timer()
        self.study_timer.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
    
        # Scale image while keeping its original proportions
        scaled_background = self.background.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
    
        # Center the image
        x = (self.width() - scaled_background.width()) // 2
        y = (self.height() - scaled_background.height()) // 2
    
        # Draw the background
        painter.drawPixmap(x, y, scaled_background)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Luma Desk")

        self.setMinimumSize(QSize(1000, 650))

        self.background_widget = BackgroundWidget()

        self.setCentralWidget(self.background_widget)

    def closeEvent(self, event):
        self.background_widget.study_timer.stop_and_save()
        self.background_widget.notes.stop_and_save()

        event.accept()