import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from luma_desk.ui.todo.task_row import TaskRow

class ToDoState:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "to_do.json"

        self.data_folder.mkdir(exist_ok=True)

        self.states = self.load()

    def load(self):
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(self.states, file, indent=4)

    def get_tasks(self):
        return self.states.get(
            "tasks", 
            [{"text": "", "completed": False} for _ in range(10)]
        )
            
    def set_tasks(self, tasks):
        self.states["tasks"] = tasks

        self.save()

  
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
            }
        """)

        # Main layout
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(0)
        self.list_layout.setContentsMargins(0, 20, 0, 5)
        
        self.list_layout.addWidget(self.title, alignment=Qt.AlignCenter)

        # Task layout
        self.task_layout = QVBoxLayout()
        self.task_layout.setSpacing(7)
        self.task_layout.setContentsMargins(15, 10, 15, 10)

        self.state = ToDoState()
        self.tasks = self.state.get_tasks()

        # Create 10 empty task rows
        for i in range(10):
            task = TaskRow(
                self.tasks[i]["text"],
                self.tasks[i]["completed"]
            )

            task.text.textChanged.connect(
                lambda text, index=i: self.task_changed(index, text)
            )

            task.task_completed.connect(
                lambda completed, index=i: self.task_completed(index, completed)
            )

            self.task_layout.addWidget(task)

        self.list_layout.addLayout(self.task_layout)

        self.setLayout(self.list_layout)

    def task_changed(self, index, text):
        self.tasks[index]["text"] = text
        self.state.set_tasks(self.tasks)

    def task_completed(self, index, completed):
        self.tasks[index]["completed"] = completed
        self.state.set_tasks(self.tasks)


        

