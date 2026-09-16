from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from luma_desk.ui.calculator.calculator_engine import (
    CalculatorError,
    evaluate,
    format_result,
)


class CalculatorWidget(QFrame):

    # text, row, column, column span, style name
    BUTTONS = [
        ("C", 0, 0, 1, "action"),
        ("⌫", 0, 1, 1, "action"),
        ("(", 0, 2, 1, "action"),
        (")", 0, 3, 1, "action"),
        ("÷", 0, 4, 1, "operator"),

        ("7", 1, 0, 1, "number"),
        ("8", 1, 1, 1, "number"),
        ("9", 1, 2, 1, "number"),
        ("^", 1, 3, 1, "operator"),
        ("×", 1, 4, 1, "operator"),

        ("4", 2, 0, 1, "number"),
        ("5", 2, 1, 1, "number"),
        ("6", 2, 2, 1, "number"),
        ("%", 2, 3, 1, "operator"),
        ("−", 2, 4, 1, "operator"),

        ("1", 3, 0, 1, "number"),
        ("2", 3, 1, 1, "number"),
        ("3", 3, 2, 1, "number"),
        (".", 3, 3, 1, "number"),
        ("+", 3, 4, 1, "operator"),

        ("0", 4, 0, 4, "number"),
        ("=", 4, 4, 1, "equals"),
    ]

    def __init__(self):
        super().__init__()

        self.last_answer = None

        # Widget styling
        self.setFixedWidth(240)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QLabel#answerLabel {
                color: rgba(255, 255, 255, 150);
                font-family: "Nunito Sans";
                font-size: 11px;
                background: transparent;
            }

            QLineEdit {
                color: white;
                background: rgba(0, 0, 0, 70);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 20px;
                font-weight: 700;
                padding: 8px;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 14px;
                font-weight: 600;
                padding: 6px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }

            QPushButton#operator {
                background: rgba(255, 255, 255, 25);
                color: rgba(255, 244, 220, 230);
            }

            QPushButton#action {
                background: rgba(0, 0, 0, 45);
                color: rgba(255, 255, 255, 190);
            }

            QPushButton#equals {
                background: rgba(232, 213, 177, 180);
                color: rgba(45, 55, 35, 255);
            }

            QPushButton#equals:hover {
                background: rgba(232, 213, 177, 220);
            }
        """)

        # Title
        self.title = QLabel("✧ Calculator")
        self.title.setAlignment(Qt.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)

        # Display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setPlaceholderText("0")
        self.display.returnPressed.connect(self.calculate)

        # Last answer / error message
        self.answer_label = QLabel("")
        self.answer_label.setObjectName("answerLabel")
        self.answer_label.setAlignment(Qt.AlignRight)

        # Buttons
        button_layout = QGridLayout()
        button_layout.setSpacing(6)
        button_layout.setContentsMargins(0, 0, 0, 0)

        for text, row, column, span, style_name in self.BUTTONS:
            button = QPushButton(text)
            button.setObjectName(style_name)
            button.setFixedHeight(34)
            button.setCursor(Qt.PointingHandCursor)
            button.setFocusPolicy(Qt.NoFocus)

            button.clicked.connect(
                lambda checked=False, value=text: self.button_pressed(value)
            )

            button_layout.addWidget(button, row, column, 1, span)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(self.title)
        layout.addWidget(self.display)
        layout.addWidget(self.answer_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    # Buttons
    def button_pressed(self, value):
        if value == "C":
            self.clear()

        elif value == "⌫":
            self.backspace()

        elif value == "=":
            self.calculate()

        else:
            self.insert(value)

    def insert(self, text):
        # Typing straight after an answer starts a new sum.
        if self.last_answer is not None and self.display.text() == self.last_answer:
            if text.isdigit() or text == "." or text == "(":
                self.display.clear()

        self.last_answer = None

        self.display.insert(text)
        self.display.setFocus()

    def backspace(self):
        self.display.backspace()
        self.display.setFocus()

    def clear(self):
        self.display.clear()
        self.answer_label.setText("")
        self.last_answer = None
        self.display.setFocus()

    # Working out
    def calculate(self):
        expression = self.display.text()

        if not expression.strip():
            return

        try:
            result = format_result(evaluate(expression))

        except CalculatorError as error:
            self.answer_label.setText(str(error))
            return

        except (ArithmeticError, ValueError):
            self.answer_label.setText("That sum couldn't be worked out.")
            return

        self.answer_label.setText(f"{expression} =")
        self.display.setText(result)
        self.last_answer = result