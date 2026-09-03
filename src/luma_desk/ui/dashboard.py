from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)

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
    def __init__(self, title, content):
        super().__init__()

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
                font-family: "Lora",
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.pin_button = QPushButton("📌")

        self.pin_button.setFixedSize(28, 28)
        self.pin_button.setCursor(Qt.PointingHandCursor)

        self.pin_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(2555, 255, 255, 150);
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

        # Drag signals
        self.drag_handle.pressed.connect(self.start_drag)
        self.drag_handle.moved.connect(self.drag)
        self.drag_handle.released.connect(self.end_drag)

    def start_drag(self, global_position):
        if self.locked:
            return

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
        self.locked = not self.locked

        if self.locked:
            self.pin_button.setText("📍")
            self.pinbutton.setToolTip("Unpin widget")
        else:
            self.pin_button.setText("📌")
            self.pin_button.setToolTip("Pin widget")        

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
        QWidget {
            background: transparent;
        }
    """)

    def add_card(self, card, x, y):
        card.setParent(self)
        card.move(x, y)
        card.show()