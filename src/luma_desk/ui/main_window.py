from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from luma_desk.ui.header import Header
from luma_desk.ui.dashboard import Dashboard
from luma_desk.ui.todo.to_do import ToDo
from luma_desk.ui.spotify.spotify_widget import SpotifyWidget
from luma_desk.ui.pomodoro.pomodoro_widget import PomodoroWidget
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

        # To Do
        self.to_do = ToDo()
        self.dashboard.add_card("todo", "To Do", self.to_do, 40, 40)

        # Spotify
        self.spotify = SpotifyWidget()
        self.dashboard.add_card("spotify", "Spotify", self.spotify, 400, 40)

        # Pomodoro
        self.pomodoro = PomodoroWidget()

        self.dashboard.add_card("pomodoro", "Pomodoro", self.pomodoro, 700, 40)

        # Study Constellation
        self.study_constellation = StudyConstellation()
        self.dashboard.add_card("study_constellation", "Study", self.study_constellation, 620, 300)

        # Floating study timer
        self.study_timer = StudyTimer()

        self.study_timer.setParent(self)

        self.study_timer.adjustSize()

        self.study_timer.show()

        self.study_timer.raise_()

        self.study_timer.study_updated.connect(self.study_constellation.refresh)

        # Main layout
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.header)
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

        self.position_study_timer()
        self.study_timer.raise_()

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

        event.accept()