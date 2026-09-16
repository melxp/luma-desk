import json
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


class StudyTimer(QFrame):

    study_updated = Signal()

    def __init__(self):
        super().__init__()

        # Data
        project_root = Path(__file__).resolve().parents[4]
        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "study.json"
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.data = self.load_data()

        # Create study.json immediately if it doesn't exist yet.
        if not self.data_file.exists():
            self.save_data()

        # Timer state
        self.running = False
        self.started_at = None

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_display)

        # Status
        self.status_label = QLabel("Ready to study")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Time
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button
        self.button = QPushButton("Start Study")
        self.button.setFixedHeight(36)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self.toggle_timer)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        layout.addWidget(self.status_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Styling
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }
        """)

        self.adjustSize()
        self.update_display()

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

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)
        except OSError as error:
            print("Could not save study data:", error)

    def add_seconds(self, seconds):
        """Used by the pomodoro timer when a focus session finishes."""

        if seconds <= 0:
            return

        today = date.today().isoformat()
        self.data[today] = self.data.get(today, 0) + int(seconds)

        self.save_data()
        self.update_display()
        self.study_updated.emit()

    # Timer controls
    def toggle_timer(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.running:
            return

        self.running = True
        self.started_at = datetime.now()

        # Make sure study.json exists.
        self.save_data()

        self.timer.start()
        self.button.setText("Stop")
        self.status_label.setText("Studying")
        self.update_display()

    def stop_timer(self):
        if not self.running:
            return

        now = datetime.now()
        elapsed = now - self.started_at
        seconds = int(elapsed.total_seconds())
        today = date.today().isoformat()
        current_total = self.data.get(today, 0)
        self.data[today] = current_total + seconds

        self.save_data()

        self.running = False
        self.started_at = None
        self.timer.stop()
        self.button.setText("Start Study")
        self.status_label.setText("Ready to study")
        self.update_display()
        self.study_updated.emit()

    # Display
    def get_today_seconds(self):
        today = date.today().isoformat()
        total = self.data.get(today, 0)

        if self.running and self.started_at:
            elapsed = datetime.now() - self.started_at
            total += int(elapsed.total_seconds())

        return total

    def update_display(self):
        total_seconds = self.get_today_seconds()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    # Application closing
    def stop_and_save(self):
        if self.running:
            self.stop_timer()
        else:
            self.save_data()