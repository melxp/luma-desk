import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)


class NotesState:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "notes.json"

        self.data_folder.mkdir(exist_ok=True)

        self.states = self.load()

    def load(self):
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(self.states, file, indent=4)
        except OSError as error:
            print("Could not save notes:", error)

    def get_text(self):
        return self.states.get("text", "")

    def set_text(self, text):
        self.states["text"] = text
        self.save()


class Notes(QFrame):
    def __init__(self):
        super().__init__()

        self.state = NotesState()

        # Widget styling
        self.setFixedWidth(260)
        self.setMinimumHeight(260)

        self.setStyleSheet("""
            QFrame#notes {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
            }

            QTextEdit {
                color: white;
                background: rgba(0, 0, 0, 60);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 12px;
                padding: 8px;
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
        """)

        self.setObjectName("notes")

        # Title
        self.title = QLabel("✎ Scratchpad")

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
            }
        """)

        # Saved indicator
        self.saved_label = QLabel("")

        self.saved_label.setStyleSheet("""
            QLabel {
                color: rgba(232, 213, 177, 200);
                font-family: "Nunito Sans";
                font-size: 10px;
            }
        """)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)

        title_row.addWidget(self.title)
        title_row.addStretch()
        title_row.addWidget(self.saved_label)

        # Text area
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Formulas, reminders, half-thoughts...")
        self.editor.setPlainText(self.state.get_text())
        self.editor.textChanged.connect(self.text_changed)

        # Saving is delayed so it doesn't write on every keypress.
        self.save_timer = QTimer(self)
        self.save_timer.setInterval(800)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_notes)

        # The "Saved" message clears itself after a moment.
        self.clear_message_timer = QTimer(self)
        self.clear_message_timer.setInterval(2000)
        self.clear_message_timer.setSingleShot(True)
        self.clear_message_timer.timeout.connect(
            lambda: self.saved_label.setText("")
        )

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 18, 15, 14)
        layout.setSpacing(10)

        layout.addLayout(title_row)
        layout.addWidget(self.editor)

        self.setLayout(layout)

    def text_changed(self):
        self.saved_label.setText("Saving...")
        self.save_timer.start()

    def save_notes(self):
        self.state.set_text(self.editor.toPlainText())

        self.saved_label.setText("Saved ✓")
        self.clear_message_timer.start()

    # Application closing
    def stop_and_save(self):
        self.save_timer.stop()
        self.state.set_text(self.editor.toPlainText())