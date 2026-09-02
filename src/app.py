from PySide6.QtCore import QSize, Qt, QTimer, QDateTime
from PySide6.QtGui import QPainter, QPixmap, QFontDatabase
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QLabel, 
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
)

def load_fonts():
    fonts = [
        "fonts/Lora/Lora-Regular.ttf",
        "fonts/Lora/Lora-SemiBold.ttf",
        "fonts/Lora/Lora-Bold.ttf",

        "fonts/Lora/Lora-Italic.ttf",
        "fonts/Lora/Lora-SemiBoldItalic.ttf",
        "fonts/Lora/Lora-BoldItalic.ttf",

        "fonts/Lora/Lora-Medium.ttf",
        "fonts/Lora/Lora-MediumItalic.ttf",

        "fonts/Nunito_Sans/Nunito-Regular.ttf",
        "fonts/Nunito_Sans/Nunito-Medium.ttf",
        "fonts/Nunito_Sans/Nunito-SemiBold.ttf",
        "fonts/Nunito_Sans/Nunito-Bold.ttf",
    ]

    for font in fonts:
        QFontDatabase.addApplicationFont(font)

class Header(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(60)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
            }
        """)

        # Left side
        logo = QLabel("✦ Luma Desk")

        # Fonts: Lora, Cormorant Garamond, Playfair Display, Nunito Sans
        logo.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 20px;
                font-weight: bold;
                font-style: italic;
                background-color: transparent;
            }
        """)

        # Navigation??


        # Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Nunito Sans";
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
            }
        """)

        # Date
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 190);
                font-family: "Nunito Sans";
                font-size: 15px;
                background-color: transparent;
            }
        """)

        # Put time and date together
        date_time_layout = QVBoxLayout()

        date_time_layout.setSpacing(0)
        date_time_layout.setContentsMargins(0, 0, 0, 0)

        date_time_layout.addWidget(self.time_label, alignment=Qt.AlignRight)
        date_time_layout.addWidget(self.date_label, alignment=Qt.AlignRight)

        date_time_widget = QWidget()
        date_time_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        date_time_widget.setLayout(date_time_layout)

        # Main header layout
        layout = QHBoxLayout()

        layout.setContentsMargins(20, 0, 20, 0)

        layout.addWidget(logo)
        #layout.addSpacing(30)
        layout.addStretch() # Push time/date to right

        layout.addWidget(date_time_widget)

        self.setLayout(layout)

        # Update clock
        self.update_time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        current = QDateTime.currentDateTime()

        self.time_label.setText(current.toString("HH:mm"))
        self.date_label.setText(current.toString("dddd, d MMMM"))


class BackgroundWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Load background image
        self.background = QPixmap("assets/background.png")

        # Header
        self.header = Header()

        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.header)

        layout.addStretch()

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
    
        # Scale image while keeping its original proportions
        scaled_background = self.background.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
    
        # Center the image
        x = (self.width() - scaled_background.width()) // 2
        y = (self.height() - scaled_background.height()) // 2
    
        # Draw the background
        painter.drawPixmap(x, y, scaled_background)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Luma Desk")

        self.setMinimumSize(QSize(1000, 650))

        background_widget = BackgroundWidget()
        
        self.setCentralWidget(background_widget)


app = QApplication([])

# Load font files
load_fonts()

window = MainWindow() 
window.showMaximized()

# Start event loop
app.exec()