from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout

class TaskRow(QFrame):
    def __init__(self, task_text):
        super().__init__()

        # ✦ ✧ ❀ ★ 
        self.bullet = QLabel("★")
        self.text = QLabel(task_text)

        self.row_layout = QHBoxLayout()

        self.row_layout.addWidget(self.bullet)
        self.row_layout.addWidget(self.text)

        self.setLayout(self.row_layout)