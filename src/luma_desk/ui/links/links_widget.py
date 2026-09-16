import json
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class LinksState:
    DEFAULT_LINKS = [
        {"name": "University portal", "url": "https://www.google.com"},
        {"name": "Google Scholar", "url": "https://scholar.google.com"},
        {"name": "Google Drive", "url": "https://drive.google.com"},
        {"name": "GitHub", "url": "https://github.com"},
    ]

    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]

        self.data_folder = project_root / "data"
        self.data_file = self.data_folder / "links.json"

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
            print("Could not save links:", error)

    def get_links(self):
        links = self.states.get("links")

        if links is None:
            return list(self.DEFAULT_LINKS)

        return [
            {
                "name": link.get("name", "Link"),
                "url": link.get("url", ""),
            }
            for link in links
            if link.get("url")
        ]

    def set_links(self, links):
        self.states["links"] = links
        self.save()


class QuickLinks(QFrame):
    def __init__(self):
        super().__init__()

        self.state = LinksState()
        self.links = self.state.get_links()

        # Widget styling
        self.setFixedWidth(200)

        self.setStyleSheet("""
            QFrame#quickLinks {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 12px;
                font-weight: 600;
                padding: 7px;
                text-align: left;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }

            QPushButton#removeButton {
                background: transparent;
                color: rgba(255, 255, 255, 110);
                font-size: 13px;
                padding: 0px;
                text-align: center;
            }

            QPushButton#removeButton:hover {
                color: rgba(255, 180, 180, 230);
                background: transparent;
            }

            QPushButton#addButton {
                background: rgba(0, 0, 0, 45);
                color: rgba(255, 255, 255, 200);
                text-align: center;
            }
        """)

        self.setObjectName("quickLinks")

        # Title
        self.title = QLabel("❖ Quick Links")
        self.title.setAlignment(Qt.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Lora";
                font-size: 15px;
                font-weight: bold;
            }
        """)

        # Link rows
        self.link_layout = QVBoxLayout()
        self.link_layout.setSpacing(6)
        self.link_layout.setContentsMargins(0, 0, 0, 0)

        # Add button
        self.add_button = QPushButton("+ Add link")
        self.add_button.setObjectName("addButton")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_link)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 18, 15, 12)
        layout.setSpacing(10)

        layout.addWidget(self.title)
        layout.addLayout(self.link_layout)
        layout.addStretch()
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        self.build_rows()

    # Rows
    def build_rows(self):
        while self.link_layout.count():
            item = self.link_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

            elif item.layout():
                self.clear_layout(item.layout())

        for position, link in enumerate(self.links):
            open_button = QPushButton(link["name"])
            open_button.setCursor(Qt.PointingHandCursor)
            open_button.setToolTip(link["url"])

            open_button.clicked.connect(
                lambda checked=False, url=link["url"]: self.open_link(url)
            )

            remove_button = QPushButton("×")
            remove_button.setObjectName("removeButton")
            remove_button.setFixedSize(18, 18)
            remove_button.setCursor(Qt.PointingHandCursor)
            remove_button.setToolTip("Remove this link")

            remove_button.clicked.connect(
                lambda checked=False, index=position: self.remove_link(index)
            )

            row_layout = QHBoxLayout()
            row_layout.setSpacing(4)
            row_layout.setContentsMargins(0, 0, 0, 0)

            row_layout.addWidget(open_button)
            row_layout.addWidget(remove_button)

            self.link_layout.addLayout(row_layout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    # Actions
    def open_link(self, url):
        webbrowser.open(url)

    def add_link(self):
        name, confirmed = QInputDialog.getText(
            self,
            "Add link",
            "Name:",
            QLineEdit.Normal,
        )

        if not confirmed or not name.strip():
            return

        url, confirmed = QInputDialog.getText(
            self,
            "Add link",
            "Address:",
            QLineEdit.Normal,
            "https://",
        )

        if not confirmed or not url.strip():
            return

        url = url.strip()

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        self.links.append({"name": name.strip(), "url": url})

        self.state.set_links(self.links)
        self.build_rows()

    def remove_link(self, index):
        if 0 <= index < len(self.links):
            del self.links[index]

            self.state.set_links(self.links)
            self.build_rows()