from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from luma_desk.ui.todo.task_row import TaskRow

class ToDo(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedSize(200, 400)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
            }

            QLabel {
                background-color: transparent;
            }
        """)

        self.title = QLabel("✦ To Do List")

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
                font-style: italic;
            }
        """)

        self.input = QLineEdit("...")

        self.list_layout = QVBoxLayout()

        self.list_layout.setSpacing(0)
        self.list_layout.setContentsMargins(0, 0, 0, 0)

        self.list_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        self.list_layout.addWidget(self.input, alignment=Qt.AlignCenter)

        self.task_layout = QVBoxLayout()

        self.task_layout.setSpacing(0)
        self.task_layout.setContentsMargins(15, 10, 15, 10)

        task = TaskRow("Finish Python assignment")

        self.task_layout.addWidget(task)

        self.list_layout.addLayout(self.task_layout)



        self.setLayout(self.list_layout)

        

