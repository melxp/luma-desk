from datetime import date

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class DeadlineRow(QFrame):

    # The title was edited, so the list needs saving.
    changed = Signal()

    # The date or the tick changed, so the list needs re-sorting too.
    reordered = Signal()

    deleted = Signal()

    def __init__(self, title, due, done):
        super().__init__()

        self.done = done

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }

            QLabel {
                background-color: transparent;
            }

            QDateEdit {
                color: rgba(255, 255, 255, 220);
                background: rgba(0, 0, 0, 55);
                border: none;
                border-radius: 6px;
                font-family: "Nunito Sans";
                font-size: 11px;
                padding: 2px 4px;
            }

            QDateEdit::drop-down {
                border: none;
                width: 12px;
            }

            QCalendarWidget QWidget {
                background-color: rgb(82, 96, 68);
                color: white;
            }

            QCalendarWidget QAbstractItemView {
                background-color: rgb(82, 96, 68);
                color: white;
                selection-background-color: rgba(232, 213, 177, 200);
                selection-color: rgb(45, 55, 35);
            }
        """)

        # Done / not done
        self.bullet = QPushButton("✦" if self.done else "✧")
        self.bullet.setFixedSize(22, 22)
        self.bullet.setCursor(Qt.PointingHandCursor)
        self.bullet.clicked.connect(self.toggle_done)

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

        # Title
        self.title = QLineEdit(title)
        self.title.setPlaceholderText("Assignment, exam, reading...")
        self.title.textChanged.connect(self.title_edited)

        # Due date
        self.due = QDateEdit()
        self.due.setCalendarPopup(True)
        self.due.setDisplayFormat("d MMM")
        self.due.setDate(QDate(due.year, due.month, due.day))
        self.due.setFixedWidth(72)
        self.due.dateChanged.connect(self.date_edited)

        # Countdown
        self.countdown = QLabel()

        # Delete
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setToolTip("Remove this deadline")
        self.delete_button.clicked.connect(self.deleted.emit)

        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(255, 255, 255, 110);
                font-size: 14px;
                padding: 0px;
            }

            QPushButton:hover {
                color: rgba(255, 180, 180, 230);
            }
        """)

        # Top line
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)
        top_layout.setContentsMargins(0, 2, 0, 0)

        top_layout.addWidget(self.bullet)
        top_layout.addWidget(self.title)
        top_layout.addWidget(self.delete_button)

        # Bottom line
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)
        bottom_layout.setContentsMargins(28, 0, 0, 4)

        bottom_layout.addWidget(self.due)
        bottom_layout.addWidget(self.countdown)
        bottom_layout.addStretch()

        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Plain)

        self.separator.setStyleSheet("""
            QFrame {
                color: rgba(255, 255, 255, 70);
            }
        """)

        # Row layout
        row_layout = QVBoxLayout()
        row_layout.setSpacing(0)
        row_layout.setContentsMargins(0, 0, 0, 0)

        row_layout.addLayout(top_layout)
        row_layout.addLayout(bottom_layout)
        row_layout.addWidget(self.separator)

        self.setLayout(row_layout)

        self.update_appearance()

    # Data
    def get_title(self):
        return self.title.text()

    def get_due(self):
        qt_date = self.due.date()
        return date(qt_date.year(), qt_date.month(), qt_date.day())

    def days_left(self):
        return (self.get_due() - date.today()).days

    # Edits
    # These slots take *arguments because Qt hands them the new text
    # or the new date, which the signals below don't carry.
    def title_edited(self, *arguments):
        self.changed.emit()

    def date_edited(self, *arguments):
        self.update_appearance()
        self.reordered.emit()

    def toggle_done(self):
        self.done = not self.done
        self.bullet.setText("✦" if self.done else "✧")

        self.update_appearance()
        self.reordered.emit()

    # Appearance
    def update_appearance(self):
        days = self.days_left()

        if self.done:
            text = "Done"
            colour = "rgba(255, 255, 255, 110)"

        elif days < 0:
            text = f"{abs(days)}d overdue"
            colour = "rgba(240, 160, 160, 230)"

        elif days == 0:
            text = "Due today"
            colour = "rgba(240, 190, 150, 240)"

        elif days == 1:
            text = "Tomorrow"
            colour = "rgba(240, 200, 160, 230)"

        elif days <= 7:
            text = f"{days} days left"
            colour = "rgba(232, 213, 177, 230)"

        else:
            text = f"{days} days left"
            colour = "rgba(255, 255, 255, 150)"

        self.countdown.setText(text)

        self.countdown.setStyleSheet(f"""
            QLabel {{
                color: {colour};
                background: transparent;
                font-family: "Nunito Sans";
                font-size: 11px;
                font-weight: 600;
            }}
        """)

        if self.done:
            self.title.setStyleSheet("""
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
            self.title.setStyleSheet("""
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