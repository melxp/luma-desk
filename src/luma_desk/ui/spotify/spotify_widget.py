import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem
)

from luma_desk.ui.spotify_manager import SpotifyManager
from luma_desk.ui.spotify.spotify_callback import SpotifyCallbackServer

class SpotifyWidget(QFrame):
    def __init__(self):
        super().__init__()

        self.spotify = SpotifyManager()
        self.callback_server = None

        self.setMinimumSize(250, 450)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 30);
                border: none;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 50)
            }
        """)

        self.title = QLabel("Spotify")
        self.title.setAlignment(Qt.AlignCenter)

        self.status = QLabel("Connect your Spotify account")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)

        self.connect_button = QPushButton("Connect Spotify")
        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.connect_button.clicked.connect(self.connect_spotify)

        self.playlist_list = QListWidget()

        self.playlist_list.setVisible(False)

        self.playlist_list.setStyleSheet("""
            QListWidget {
                color: white;
                background: rgba(0, 0, 0, 60);
                border: none;
                border-radius: 8px;
            }

            QListWidget::item {
                padding: 8px;
            }

            QListWidget::item:hover {
                background: rgba(255, 255, 255, 30);
            }

            QListWidget::item:selected {
                background: rgba(255, 255, 255, 45);
            }
        """)

        self.playlist_list.itemClicked.connect(
        self.load_playlist_tracks
)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.playlist_list)
        layout.addStretch()
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def connect_spotify(self):

        self.status.setText("Opening Spotify...")
        self.connect_button.setEnabled(False)

        self.callback_server = SpotifyCallbackServer(port=8888)

        self.callback_server.callback_received.connect(self.spotify_callback)
        self.callback_server.callback_error.connect(self.spotify_error)

        self.callback_server.start()

        auth_url = self.spotify.create_authorization_url()

        webbrowser.open(auth_url)

    def spotify_callback(self, code, state):

        if state != self.spotify.state:
            self.spotify_error("state_mismatch")
            return 

        try: 

            self.status.setText("Finishing Spotify login...")
            self.spotify.exchange_code(code)
            self.status.setText("Spotify connected!")
            self.connect_button.setText("Connected")
            self.load_playlists()

        except Exception as error:

            print("Spotify token error: ", error)
            self.spotify_error("token_exchange_failed")


    def load_playlists(self):

        try:

            playlist_data = self.spotify.get_playlists()
            self.playlist_list.clear()
            playlists = playlist_data.get("items", [])

            for playlist in playlists:

                name = playlist.get("name", "Unnamed playlist")
                playlist_id = playlist.get("id")

                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, playlist_id)

                self.playlist_list.addItem(item)

            self.playlist_list.setVisible(True)

            self.status.setText(f"{len(playlists)} playlists loaded")

        except Exception as error:

            print("Playlist loading error:", error)

            self.status.setText("Could not load playlists.")


    def load_playlist_tracks(self, item):

        playlist_id = item.data(Qt.UserRole)

        if not playlist_id:
            return

        try:

            playlist_data = self.spotify.get_playlist_items(playlist_id)
            
            self.playlist_list.clear()

            tracks = playlist_data.get("items", [])

            for playlist_item in tracks:

                track = playlist_item.get("track")

                if not track:
                    continue

                if track.get("type") != "track":
                    continue

                track_name = track.get("name", "Unknown track")

                artists = track.get("artists", [])

                artist_names = ", ".join(
                    artist.get("name", "")
                    for artist in artists
                )

                text = f"{track_name} — {artist_names}"

                list_item = QListWidgetItem(text)
                list_item.setData(Qt.UserRole, track.get("uri"))

                self.playlist_list.addItem(list_item)

            self.status.setText(f"{len(tracks)} items loaded")

        except Exception as error:

            print("Track loading error:", error)

            self.status.setText("Could not load playlist.")

    def spotify_error(self, error):

        print("Spotify authorization error: ", error)
        self.status.setText("Spotify connection failed.")
        self.connect_button.setEnabled(True)