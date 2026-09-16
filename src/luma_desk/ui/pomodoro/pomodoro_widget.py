import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
)


class PomodoroState:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "pomodoro.json"

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
            print("Could not save pomodoro settings:", error)

    def get(self, key, fallback):
        value = self.states.get(key, fallback)

        return value if isinstance(value, type(fallback)) else fallback

    def set_settings(self, work, short, long, auto_continue):
        self.states["work_minutes"] = work
        self.states["short_break_minutes"] = short
        self.states["long_break_minutes"] = long
        self.states["auto_continue"] = auto_continue

        self.save()


class PomodoroWidget(QFrame):

    # Sent when a full focus session finishes, so the study
    # tracker can count the time.
    focus_completed = Signal(int)

    def __init__(self):
        super().__init__()

        self.state = PomodoroState()

        # Set default timings
        self.work_minutes = self.state.get("work_minutes", 25)
        self.short_break_minutes = self.state.get("short_break_minutes", 5)
        self.long_break_minutes = self.state.get("long_break_minutes", 15)

        self.sessions_before_long_break = 4

        # Timer state
        self.remaining = self.work_minutes * 60

        self.running = False
        self.is_work_session = True
        self.session_number = 1
        self.completed_sessions = 0

        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        # Main widget styling
        self.setObjectName("pomodoro")

        self.setFixedWidth(220)

        self.setStyleSheet("""
            QFrame#pomodoro {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QLabel#sessionLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }

            QLabel#timeLabel {
                color: white;
                font-size: 42px;
                font-weight: bold;
                background: transparent;
            }

            QLabel#nextLabel {
                color: rgba(255, 255, 255, 160);
                font-size: 11px;
                background: transparent;
            }

            QLabel#settingsLabel {
                color: rgba(255, 255, 255, 180);
                font-size: 10px;
                background: transparent;
            }

            QLabel#countLabel {
                color: rgba(232, 213, 177, 220);
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }

            QCheckBox {
                color: rgba(255, 255, 255, 180);
                font-size: 10px;
                background: transparent;
            }

            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border-radius: 3px;
                background: rgba(255, 255, 255, 45);
            }

            QCheckBox::indicator:checked {
                background: rgba(232, 213, 177, 220);
            }

            QComboBox {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 11px;
            }

            QComboBox:hover {
                background: rgba(255, 255, 255, 75);
            }

            QComboBox:disabled {
                color: rgba(255, 255, 255, 100);
                background: rgba(255, 255, 255, 15);
            }

            QComboBox QAbstractItemView {
                color: white;
                background: rgba(82, 96, 68, 240);
                border: none;
                selection-background-color: rgba(255, 255, 255, 45);
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }

            QPushButton:disabled {
                color: rgba(255, 255, 255, 100);
                background: rgba(255, 255, 255, 15);
            }
        """)

        # Session label
        self.session_label = QLabel("Focus Session 1")
        self.session_label.setObjectName("sessionLabel")
        self.session_label.setAlignment(Qt.AlignCenter)

        # Timer display
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)

        # Next session label
        self.next_label = QLabel()
        self.next_label.setObjectName("nextLabel")
        self.next_label.setAlignment(Qt.AlignCenter)

        # Completed sessions
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        self.count_label.setAlignment(Qt.AlignCenter)

        # Settings
        self.settings_label = QLabel("Focus")
        self.settings_label.setObjectName("settingsLabel")

        self.work_selector = self.create_duration_selector(
            [15, 20, 25, 30, 45, 50, 60, 90],
            self.work_minutes
        )

        self.short_selector = self.create_duration_selector(
            [3, 5, 10, 15],
            self.short_break_minutes
        )

        self.long_selector = self.create_duration_selector(
            [10, 15, 20, 30],
            self.long_break_minutes
        )

        self.work_selector.currentIndexChanged.connect(
            self.settings_changed
        )

        self.short_selector.currentIndexChanged.connect(
            self.settings_changed
        )

        self.long_selector.currentIndexChanged.connect(
            self.settings_changed
        )

        # Roll straight into the next session
        self.auto_continue = QCheckBox("Start the next one automatically")
        self.auto_continue.setChecked(self.state.get("auto_continue", True))
        self.auto_continue.setCursor(Qt.PointingHandCursor)
        self.auto_continue.stateChanged.connect(self.save_settings)

        # Focus row
        focus_row = QHBoxLayout()
        focus_row.setSpacing(5)

        focus_label = QLabel("Focus")
        focus_label.setObjectName("settingsLabel")

        focus_row.addWidget(focus_label)
        focus_row.addStretch()
        focus_row.addWidget(self.work_selector)

        # Short break row
        short_row = QHBoxLayout()
        short_row.setSpacing(5)

        short_label = QLabel("Short break")
        short_label.setObjectName("settingsLabel")

        short_row.addWidget(short_label)
        short_row.addStretch()
        short_row.addWidget(self.short_selector)

        # Long break row
        long_row = QHBoxLayout()
        long_row.setSpacing(5)

        long_label = QLabel("Long break")
        long_label.setObjectName("settingsLabel")

        long_row.addWidget(long_label)
        long_row.addStretch()
        long_row.addWidget(self.long_selector)

        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.toggle_timer)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setCursor(Qt.PointingHandCursor)
        self.skip_button.setToolTip("Jump to the next session")
        self.skip_button.clicked.connect(self.skip_session)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_timer)

        button_row = QHBoxLayout()
        button_row.setSpacing(6)

        button_row.addWidget(self.start_button)
        button_row.addWidget(self.skip_button)
        button_row.addWidget(self.reset_button)

        # Main layout
        layout = QVBoxLayout()

        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(6)

        layout.addWidget(self.session_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.next_label)
        layout.addWidget(self.count_label)

        layout.addSpacing(4)

        layout.addLayout(focus_row)
        layout.addLayout(short_row)
        layout.addLayout(long_row)
        layout.addWidget(self.auto_continue)

        layout.addSpacing(4)

        layout.addLayout(button_row)

        self.setLayout(layout)

        self.update_display()

    # Helpers
    def create_duration_selector(self, values, current):
        selector = QComboBox()

        for value in values:
            selector.addItem(f"{value} min", value)

        if current not in values:
            current = values[0]

        index = values.index(current)
        selector.setCurrentIndex(index)

        return selector

    # Settings
    def save_settings(self):
        self.state.set_settings(
            self.work_minutes,
            self.short_break_minutes,
            self.long_break_minutes,
            self.auto_continue.isChecked(),
        )

    def settings_changed(self):
        # Don't change the current timer while it's running.
        if self.running:
            return

        self.work_minutes = self.work_selector.currentData()
        self.short_break_minutes = self.short_selector.currentData()
        self.long_break_minutes = self.long_selector.currentData()

        self.save_settings()

        self.reset_timer()

    # Timer controls
    def toggle_timer(self):
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.running = True

        self.timer.start()

        self.start_button.setText("Pause")

        # Don't allow settings to change during a session
        self.work_selector.setEnabled(False)
        self.short_selector.setEnabled(False)
        self.long_selector.setEnabled(False)

    def pause_timer(self):
        self.running = False

        self.timer.stop()

        self.start_button.setText("Start")

        self.work_selector.setEnabled(True)
        self.short_selector.setEnabled(True)
        self.long_selector.setEnabled(True)

    def reset_timer(self):
        self.pause_timer()

        self.is_work_session = True
        self.session_number = 1

        self.remaining = self.work_minutes * 60

        self.update_display()

    def skip_session(self):
        # Skipping doesn't count as studying.
        self.switch_session(finished=False)

    # Timer
    def tick(self):
        self.remaining -= 1

        if self.remaining <= 0:
            self.switch_session(finished=True)
            return

        self.update_display()

    def switch_session(self, finished):
        keep_going = self.running and self.auto_continue.isChecked()

        self.pause_timer()

        if self.is_work_session:

            if finished:
                self.completed_sessions += 1

                # Let the study tracker count this focus time.
                self.focus_completed.emit(self.work_minutes * 60)

                QApplication.beep()

            # Focus -> Break
            if self.session_number >= self.sessions_before_long_break:
                # After session 4, take long break
                self.is_work_session = False
                self.remaining = self.long_break_minutes * 60

            else:
                # Normal short break
                self.is_work_session = False
                self.remaining = self.short_break_minutes * 60

        else:

            if finished:
                QApplication.beep()

            # Break -> Focus
            if self.session_number >= self.sessions_before_long_break:
                # Long break finished.
                # Start a new cycle.
                self.session_number = 1

            else:
                self.session_number += 1

            self.is_work_session = True
            self.remaining = self.work_minutes * 60

        self.update_display()

        if keep_going:
            self.start_timer()

    # Display
    def update_display(self):
        minutes = self.remaining // 60
        seconds = self.remaining % 60

        self.time_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        if self.completed_sessions == 1:
            self.count_label.setText("✦ 1 session finished")
        elif self.completed_sessions > 1:
            self.count_label.setText(
                f"✦ {self.completed_sessions} sessions finished"
            )
        else:
            self.count_label.setText("")

        # Current session
        if self.is_work_session:

            self.session_label.setText(
                f"Focus Session {self.session_number}"
            )

            # Determine next break
            if self.session_number >= self.sessions_before_long_break:
                self.next_label.setText(
                    "Next: Long Break"
                )
            else:
                self.next_label.setText(
                    "Next: Short Break"
                )

        else:

            if self.session_number >= self.sessions_before_long_break:
                self.session_label.setText(
                    "Long Break"
                )

                self.next_label.setText(
                    "Next: Focus Session 1"
                )

            else:
                self.session_label.setText(
                    "Short Break"
                )

                self.next_label.setText(
                    f"Next: Focus Session {self.session_number + 1}"
                )