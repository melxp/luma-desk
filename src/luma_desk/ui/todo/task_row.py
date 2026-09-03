from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, 
    QPushButton,
    QLabel, 
    QHBoxLayout, 
    QVBoxLayout, 
    QLineEdit,
)

class TaskRow(QFrame):

    task_completed = Signal(bool)

    def __init__(self, task_text, completed):
        super().__init__()

        self.completed = completed

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
            QLabel {
                background-color: transparent;
            }
        """)

        if self.completed:
            bullet = "✦"
        else:
            bullet = "✧"

        self.bullet = QPushButton(bullet)
        self.bullet.setFixedSize(22, 22)
        self.bullet.clicked.connect(self.toggle_completed)

        self.bullet.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-family: "Lora";
                font-size: 13px;
                padding: 0px;
            }

            QPushButton:hover {
                color: rgba(255, 255, 255, 180);
            }
        """)

        self.bullet.setCursor(Qt.PointingHandCursor)

        # Editabe task text
        self.text = QLineEdit(task_text)
        self.text.setPlaceholderText("Add a task...")

        self.text.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
                font-family: "Nunito";
                font-size: 12px;
                font-weight: 600;
                padding: 0px;
            }
        """)

        self.update_appearance()

        # Task content
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(6)
        self.content_layout.setContentsMargins(0, 4, 0, 4)

        self.content_layout.addWidget(self.bullet)
        self.content_layout.addWidget(self.text)

        # Line separator
        self.separator =  QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Plain)

        self.separator.setStyleSheet("""
            QFrame {
                color: rgba(255, 255, 255, 70);
            }
        """)

        # Row layout
        self.row_layout = QVBoxLayout()
        self.row_layout.setSpacing(0)
        self.row_layout.setContentsMargins(0, 0, 0, 0)

        self.row_layout.addLayout(self.content_layout)
        self.row_layout.addWidget(self.separator)

        self.setLayout(self.row_layout)

    def toggle_completed(self):
        self.completed = not self.completed

        self.update_appearance()

        self.task_completed.emit(self.completed)

    def update_appearance(self):
        if self.completed:
            self.bullet.setText("✦")

            self.text.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 120);
                    font-family: "Nunito";
                    font-size: 12px;
                    font-weight: 600;
                    text-decoration: line-through;
                    padding: 0px;
                }
            """)
        else:
            self.bullet.setText("✧")

            self.text.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    border: none;
                    color: white;
                    font-family: "Nunito";
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0px;
                }
            """)