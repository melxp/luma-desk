import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
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
        tasks = self.states.get("tasks", [])

        # Older saves always held ten rows, most of them blank.
        return [
            {
                "text": task.get("text", ""),
                "completed": bool(task.get("completed", False)),
            }
            for task in tasks
            if task.get("text", "").strip()
        ]

    def set_tasks(self, tasks):
        self.states["tasks"] = tasks

        self.save()

  
class ToDo(QFrame):
    def __init__(self):
        super().__init__()

        self.state = ToDoState()
        self.tasks = self.state.get_tasks()
        self.rows = []

        self.setFixedWidth(220)
        self.setMinimumHeight(400)

        self.setStyleSheet("""
            QFrame#toDo {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 70);
                border-radius: 3px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 11px;
                padding: 7px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }

            QPushButton#clearButton {
                background: rgba(0, 0, 0, 45);
                color: rgba(255, 255, 255, 190);
            }
        """)

        self.setObjectName("toDo")

        self.title = QLabel("❀ To Do List")
        self.title.setAlignment(Qt.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
            }
        """)

        # Progress
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)

        self.progress_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 150);
                font-family: "Nunito Sans";
                font-size: 11px;
            }
        """)

        # Task layout
        self.task_layout = QVBoxLayout()
        self.task_layout.setSpacing(5)
        self.task_layout.setContentsMargins(0, 0, 6, 0)
        self.task_layout.addStretch()

        self.task_container = QWidget()
        self.task_container.setStyleSheet("background: transparent;")
        self.task_container.setLayout(self.task_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.task_container)

        # Buttons
        self.add_button = QPushButton("+ Add task")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_task)

        self.clear_button = QPushButton("Clear done")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_completed)

        button_row = QHBoxLayout()
        button_row.setSpacing(6)
        button_row.setContentsMargins(0, 0, 0, 0)

        button_row.addWidget(self.add_button)
        button_row.addWidget(self.clear_button)

        # Main layout
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(15, 18, 15, 12)

        self.list_layout.addWidget(self.title)
        self.list_layout.addWidget(self.progress_label)
        self.list_layout.addWidget(self.scroll_area)
        self.list_layout.addLayout(button_row)

        self.setLayout(self.list_layout)

        self.build_rows()

    # Rows
    def build_rows(self):
        for row in self.rows:
            self.task_layout.removeWidget(row)
            row.deleteLater()

        self.rows = []

        for position, task in enumerate(self.tasks):
            row = TaskRow(task["text"], task["completed"])

            row.text.textChanged.connect(
                lambda text, row=row: self.task_changed(row, text)
            )

            row.task_completed.connect(
                lambda completed, row=row: self.task_completed(row, completed)
            )

            row.deleted.connect(
                lambda row=row: self.delete_task(row)
            )

            self.task_layout.insertWidget(position, row)
            self.rows.append(row)

        self.update_progress()

    def update_progress(self):
        if not self.tasks:
            self.progress_label.setText("Nothing on the list yet")
            return

        done = sum(1 for task in self.tasks if task["completed"])

        self.progress_label.setText(f"{done} of {len(self.tasks)} done")

    # Task changes
    def task_changed(self, row, text):
        if row not in self.rows:
            return

        self.tasks[self.rows.index(row)]["text"] = text
        self.state.set_tasks(self.tasks)

    def task_completed(self, row, completed):
        if row not in self.rows:
            return

        self.tasks[self.rows.index(row)]["completed"] = completed
        self.state.set_tasks(self.tasks)
        self.update_progress()

    def add_task(self):
        self.tasks.append({"text": "", "completed": False})
        self.state.set_tasks(self.tasks)

        self.build_rows()

        if self.rows:
            self.rows[-1].text.setFocus()

    def delete_task(self, row):
        if row not in self.rows:
            return

        index = self.rows.index(row)

        del self.tasks[index]
        self.rows.remove(row)

        self.task_layout.removeWidget(row)
        row.deleteLater()

        self.state.set_tasks(self.tasks)
        self.update_progress()

    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task["completed"]]

        self.state.set_tasks(self.tasks)
        self.build_rows()