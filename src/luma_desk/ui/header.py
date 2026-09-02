from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class Header(QFrame):
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

        # Navigation??


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

        layout.addWidget(logo)
        #layout.addSpacing(30)
        layout.addStretch() # Push time/date to right

        layout.addWidget(date_time_widget)

        self.setLayout(layout)

        # Update clock
        self.update_time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        current = QDateTime.currentDateTime()

        self.time_label.setText(current.toString("HH:mm"))
        self.date_label.setText(current.toString("dddd, d MMMM"))