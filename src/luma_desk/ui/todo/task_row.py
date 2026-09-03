from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit

class TaskRow(QFrame):
    def __init__(self, task_text, bullet):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
            QLabel {
                background-color: transparent;
            }
        """)

        # ✦ ✧ ❀ ★ 
        self.bullet = QLabel(bullet)

        self.bullet.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 13px;
            }
        """)

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
                padding: 0px;
            }
        """)

        # Task content
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(8)
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