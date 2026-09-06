from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from luma_desk.ui.header import Header
from luma_desk.ui.dashboard import Dashboard
from luma_desk.ui.todo.to_do import ToDo
from luma_desk.ui.spotify.spotify_widget import SpotifyWidget


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

        # Main layout
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.header)
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

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

        background_widget = BackgroundWidget()
        
        self.setCentralWidget(background_widget)