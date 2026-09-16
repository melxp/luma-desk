from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class QuoteCard(QFrame):

    QUOTES = [
        ("Little by little, one travels far.", "Proverb"),
        ("Well begun is half done.", "Aristotle"),
        ("It always seems impossible until it's done.", "Nelson Mandela"),
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("Nothing in life is to be feared, it is only to be understood.", "Marie Curie"),
        ("A year from now you may wish you had started today.", "Karen Lamb"),
        ("Fall seven times, stand up eight.", "Japanese proverb"),
        ("Simplicity is the soul of efficiency.", "Austin Freeman"),
        ("Done is better than perfect.", "Anonymous"),
        ("The best way out is always through.", "Robert Frost"),
        ("Slow is smooth, smooth is fast.", "Anonymous"),
        ("Energy and persistence conquer all things.", "Benjamin Franklin"),
        ("You don't have to be great to start.", "Zig Ziglar"),
        ("Order and simplification are the first steps toward mastery.", "Thomas Mann"),
    ]

    def __init__(self):
        super().__init__()

        # A different quote each day, then the button moves on.
        self.index = date.today().toordinal() % len(self.QUOTES)

        # Widget styling
        self.setFixedWidth(260)

        self.setStyleSheet("""
            QFrame#quoteCard {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
            }

            QPushButton {
                color: rgba(255, 255, 255, 190);
                background: rgba(255, 255, 255, 30);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 11px;
                padding: 6px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 65);
                color: white;
            }
        """)

        self.setObjectName("quoteCard")

        # Quote
        self.quote_label = QLabel()
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)

        self.quote_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 14px;
                font-style: italic;
            }
        """)

        # Author
        self.author_label = QLabel()
        self.author_label.setAlignment(Qt.AlignCenter)

        self.author_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 160);
                font-family: "Nunito Sans";
                font-size: 11px;
                font-weight: 600;
            }
        """)

        # New quote
        self.refresh_button = QPushButton("Another one")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.next_quote)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(8)

        layout.addWidget(self.quote_label)
        layout.addWidget(self.author_label)
        layout.addStretch()
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

        self.show_quote()

    def show_quote(self):
        quote, author = self.QUOTES[self.index]

        self.quote_label.setText(f"\u201c{quote}\u201d")
        self.author_label.setText(f"— {author}")

    def next_quote(self):
        self.index = (self.index + 1) % len(self.QUOTES)
        self.show_quote()