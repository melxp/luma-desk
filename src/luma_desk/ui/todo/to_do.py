from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
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

        self.title = QLabel("❀ To Do List")

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
                font-style: italic;
            }
        """)

        # Main layout
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(0)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_layout.addWidget(self.title, alignment=Qt.AlignCenter)

        # Task layout
        self.task_layout = QVBoxLayout()
        self.task_layout.setSpacing(7)
        self.task_layout.setContentsMargins(15, 10, 15, 10)

        # Create 10 empty task rows
        for i in range(10):
            bullet = "✦" if i % 2 == 0 else "✧"
            task = TaskRow("", bullet)
            self.task_layout.addWidget(task)

        self.list_layout.addLayout(self.task_layout)

        self.setLayout(self.list_layout)



        

