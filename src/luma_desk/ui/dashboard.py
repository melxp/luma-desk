import json
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)



class DashboardState:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "dashboard.json"

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

    def get(self, widget_id):
        return self.states.get(widget_id)

    def set(self, widget_id, x, y):
        self.states[widget_id] = {
            "pinned": True,
            "x": x,
            "y": y,
        }

        self.save()

    def unpin(self, widget_id):
        self.states[widget_id] = {
            "pinned": False
        }

        self.save()

    
class DragHandle(QLabel):
    pressed = Signal(QPoint)
    moved = Signal(QPoint)
    released = Signal()

    def __init__(self):
        super().__init__("⋮⋮")

        self.setFixedHeight(30)
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 180);
                background: transparent;
                font-size: 14px;
            }
            
            QLabel:hover {
                color: white;
            }
        """)

        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.pressed.emit(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.moved.emit(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.released.emit()


class DraggableCard(QFrame):
    def __init__(self, widget_id, title, content, default_x, default_y, state):
        super().__init__()

        self.widget_id = widget_id
        self.default_x = default_x
        self.default_y = default_y
        self.state = state

        self.locked = False
        self.drag_offset = QPoint()

        self.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)

        # Card header
        self.drag_handle = DragHandle()

        self.title = QLabel(title)

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.pin_button = QPushButton("📌")

        self.pin_button.setFixedSize(28, 28)
        self.pin_button.setCursor(Qt.PointingHandCursor)
        self.pin_button.setToolTip("Pin widget")

        self.pin_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 150);
                font-size: 12px;
            }

            QPushButton:hover {
                color: white;
            }
        """)

        self.pin_button.clicked.connect(self.toggle_pin)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(2)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_layout.addWidget(self.drag_handle)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_button)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(content)

        # Card layout
        card_layout = QVBoxLayout()
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addLayout(header_layout)
        card_layout.addLayout(content_layout)

        self.setLayout(card_layout)

        self.adjustSize()

        # Restore saved state
        saved_state = self.state.get(self.widget_id)

        if saved_state and saved_state.get("pinned"):
            self.locked = True
            self.move(saved_state["x"], saved_state["y"])
            self.pin_button.setText("📍")
            self.pin_button.setToolTip("Unpin widget")
        else:
            self.move(self.default_x, self.default_y)

        # Drag signals
        self.drag_handle.pressed.connect(self.start_drag)
        self.drag_handle.moved.connect(self.drag)
        self.drag_handle.released.connect(self.end_drag)

    def start_drag(self, global_position):
        if self.locked:
            return

        # The card being moved should sit above the others.
        self.raise_()

        self.drag_offset = (global_position - self.mapToGlobal(QPoint(0, 0)))

    def drag(self, global_position):
        if self.locked:
            return

        parent = self.parentWidget()

        new_position = (parent.mapFromGlobal(global_position) - self.drag_offset)

        # Keep the card inside the dashboard
        x = max(0, new_position.x())
        y = max(0, new_position.y())

        max_x = parent.width() - self.width()
        max_y = parent.height() - self.height()

        x = min(x, max_x)
        y = min(y, max_y)

        self.move(x, y)

    def end_drag(self):
        pass

    def toggle_pin(self):
        if self.locked:
            self.locked = False # Unpin

            self.pin_button.setText("📌")
            self.pin_button.setToolTip("Pin widget")   

            self.state.unpin(self.widget_id)

        else:
            self.locked = True # Pin
            self.state.set(self.widget_id, self.x(), self.y())

            self.pin_button.setText("📍")
            self.pin_button.setToolTip("Unpin widget")
   

class Dashboard(QWidget):

    MARGIN = 20
    SPACING = 20

    def __init__(self):
        super().__init__()

        self.state = DashboardState()

        self.cards = []
        self.arranged = False

        self.setStyleSheet("""
        QWidget {
            background: transparent;
        }
    """)

    def add_card(self, widget_id, title, content, x, y):
        card = DraggableCard(widget_id, title, content, x, y, self.state)

        card.setParent(self)
        card.show()

        self.cards.append(card)

        return card

    # Tidying
    def tidy(self):
        """Flow every unpinned card into neat rows. Pinned cards stay put."""

        x = self.MARGIN
        y = self.MARGIN
        row_height = 0

        for card in self.cards:

            if card.locked:
                continue

            card.adjustSize()

            # Start a new row when this one runs out of space.
            if x > self.MARGIN and x + card.width() > self.width() - self.MARGIN:
                x = self.MARGIN
                y += row_height + self.SPACING
                row_height = 0

            card.move(x, y)

            x += card.width() + self.SPACING
            row_height = max(row_height, card.height())

    def showEvent(self, event):
        super().showEvent(event)

        # Lay the cards out once, the first time there's a real
        # window size to work with.
        if not self.arranged:
            self.arranged = True
            self.tidy()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not self.arranged:
            self.arranged = True
            self.tidy()