from PySide6.QtCore import Qt, QDateTime, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
 
 
class Header(QFrame):
 
    tidy_requested = Signal()
 
    def __init__(self):
        super().__init__()
 
        self.setFixedHeight(60)
 
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
            }
 
            QLabel {
                background-color: transparent;
            }
 
            QPushButton {
                color: rgba(255, 255, 255, 200);
                background: rgba(255, 255, 255, 35);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 12px;
                padding: 6px 12px;
            }
 
            QPushButton:hover {
                background: rgba(255, 255, 255, 70);
                color: white;
            }
        """)
 
        # Left side
        logo = QLabel("✦ Luma Desk")
 
        logo.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 20px;
                font-weight: bold;
                font-style: italic;
            }
        """)
 
        # Today's study total
        self.study_label = QLabel()
 
        self.study_label.setStyleSheet("""
            QLabel {
                color: rgba(232, 213, 177, 230);
                font-family: "Nunito Sans";
                font-size: 13px;
                font-weight: 700;
            }
        """)
 
        # Tidy the dashboard
        self.tidy_button = QPushButton("Tidy widgets")
        self.tidy_button.setCursor(Qt.PointingHandCursor)
        self.tidy_button.setToolTip("Line the unpinned widgets back up")
        self.tidy_button.clicked.connect(self.tidy_requested.emit)
 
        # Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Nunito Sans";
                font-size: 18px;
                font-weight: 700;
            }
        """)
 
        # Date
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 190);
                font-family: "Nunito Sans";
                font-size: 15px;
                font-weight: 400;
            }
        """)
 
        # Put time and date together
        date_time_layout = QVBoxLayout()
 
        date_time_layout.setSpacing(0)
        date_time_layout.setContentsMargins(0, 0, 0, 0)
 
        date_time_layout.addWidget(self.time_label, alignment=Qt.AlignRight)
        date_time_layout.addWidget(self.date_label, alignment=Qt.AlignRight)
 
        date_time_widget = QWidget()
        date_time_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        date_time_widget.setLayout(date_time_layout)
 
        # Main header layout
        layout = QHBoxLayout()
 
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
 
        layout.addWidget(logo)
        layout.addStretch() # Push time/date to right
 
        layout.addWidget(self.study_label)
        layout.addWidget(self.tidy_button)
        layout.addWidget(date_time_widget)
 
        self.setLayout(layout)
 
        self.set_study_seconds(0)
 
        # Update clock
        self.update_time()
 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
 
    def update_time(self):
        current = QDateTime.currentDateTime()
 
        self.time_label.setText(current.toString("HH:mm"))
        self.date_label.setText(current.toString("dddd, d MMMM"))
 
    def set_study_seconds(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
 
        if hours > 0:
            total = f"{hours}h {minutes}m"
        else:
            total = f"{minutes}m"
 
        self.study_label.setText(f"✦ {total} studied today")