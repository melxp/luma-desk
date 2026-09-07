import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem
)

from luma_desk.ui.spotify_manager import SpotifyManager
from luma_desk.ui.spotify.spotify_callback import SpotifyCallbackServer

class SpotifyWidget(QFrame):
    def __init__(self):
        super().__init__()

        # Spotify manager
        self.spotify = SpotifyManager()
        self.callback_server = None

        # Widget styling
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

            QListWidget {
                color: white;
                background: rgba(0, 0, 0, 80);
                border: none;
                border-radius: 8px;
                font-size: 12px;
            }
            
            QListWidget::item {
                color: white;
                background: transparent;
                padding: 8px;
                min-height: 20px;
            }
            
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 30);
            }
            
            QListWidget::item:selected {
                color: white;
                background: rgba(255, 255, 255, 45);
            }       
        """)

        # Title
        self.title = QLabel("Spotify")
        self.title.setAlignment(Qt.AlignCenter)

        # Status
        self.status = QLabel("Connect your Spotify account")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)

        # Connect button
        self.connect_button = QPushButton("Connect Spotify")
        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.connect_button.clicked.connect(self.connect_spotify)

        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.setVisible(False)
        self.playlist_list.itemClicked.connect(self.load_playlist_tracks)

        # Track list
        self.track_list = QListWidget()
        self.track_list.setVisible(False)
        self.track_list.itemClicked.connect(self.track_clicked)

        # Back button
        self.back_button = QPushButton("<- Playlists")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setVisible(False)
        self.back_button.clicked.connect(self.show_playlists)

        # Playback buttons
        self.previous_button = QPushButton("⏮")
        self.play_pause_button = QPushButton("▶")
        self.next_button = QPushButton("⏭")

        for button in (self.previous_button, self.play_pause_button, self.next_button):
            button.setCursor(Qt.PointingHandCursor)
            button.setEnabled(False)
            button.setMinimumSize(55, 40)

        self.previous_button.clicked.connect(
            self.previous_track
        )

        self.play_pause_button.clicked.connect(
            self.toggle_playback
        )

        self.next_button.clicked.connect(
            self.next_track
        )

        self.playback_layout = QHBoxLayout()
        self.playback_layout.setContentsMargins(0, 0, 0, 0)
        self.playback_layout.setSpacing(8)

        self.playback_layout.addWidget(self.previous_button)
        self.playback_layout.addWidget(self.play_pause_button)
        self.playback_layout.addWidget(self.next_button)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.playlist_list)
        layout.addWidget(self.track_list)
        layout.addWidget(self.back_button)
        layout.addLayout(self.playback_layout)
        layout.addStretch()
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

        # Clean shutdown
        app = QApplication.instance()

        if app:
            app.aboutToQuit.connect(self.shutdown)

    # Spotify authentication
    def connect_spotify(self):

        self.status.setText("Opening Spotify...")
        self.connect_button.setEnabled(False)

        if self.callback_server:
            self.callback_server.stop()
            self.callback_server = None

        self.callback_server = SpotifyCallbackServer(port=8888)

        self.callback_server.callback_received.connect(self.spotify_callback)
        self.callback_server.callback_error.connect(self.spotify_error)

        self.callback_server.start()

        auth_url = self.spotify.create_authorization_url()

        webbrowser.open(auth_url)


    def spotify_callback(self, code, state):

        # Protect against an unexpected OAuth response
        if state != self.spotify.state:
            self.spotify_error("state_mismatch")
            return 

        try: 

            self.status.setText("Finishing Spotify login...")
            self.spotify.exchange_code(code) # Exchange auth code for tokens
            self.status.setText("Spotify connected!")
            self.connect_button.setText("Connected")

            self.enable_playback_controls(True)

            # Load user's playlists
            self.load_playlists()

        except Exception as error:

            print("Spotify token error: ", repr(error))
            self.spotify_error("token_exchange_failed")

    def spotify_error(self, error):

        print("Spotify authorization error: ", error)
        self.status.setText("Spotify connection failed.")
        self.connect_button.setEnabled(True)
        self.enable_playback_controls(False)

    def enable_playback_controls(self, enabled):

        print("Playback controls enabled: ", enabled)
        
        self.previous_button.setEnabled(enabled)
        self.play_pause_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)


    # Playlists
    def load_playlists(self):

        try:

            playlist_data = self.spotify.get_playlists()
            self.playlist_list.clear()
            playlists = playlist_data.get("items", [])

            for playlist in playlists:

                name = playlist.get("name", "Unnamed playlist")
                playlist_id = playlist.get("id")

                if not playlist_id:
                    continue

                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, playlist_id)

                self.playlist_list.addItem(item)

            self.playlist_list.setVisible(True)
            self.track_list.setVisible(False)
            self.back_button.setVisible(False)

            self.status.setText(f"{len(playlists)} playlists loaded")

        except Exception as error:

            print("Playlist loading error:", repr(error))

            self.status.setText("Could not load playlists.")


    # Playlist tracks
    def load_playlist_tracks(self, item):

        playlist_id = item.data(Qt.UserRole)

        if not playlist_id:
            return

        try:

            playlist_data = self.spotify.get_playlist_items(playlist_id)
            
            self.track_list.clear()

            tracks = playlist_data.get("items", [])

            displayed_tracks = 0

            for playlist_item in tracks:

                track = playlist_item.get("item")

                if not track:
                    continue

                # Ignore non-track items
                if track.get("type") != "track":
                    continue

                if track.get("is_playable") is False:
                    continue

                track_name = track.get("name", "Unknown track")

                artists = track.get("artists", [])

                artist_names = ", ".join(
                    artist.get("name", "")
                    for artist in artists
                )

                text = (
                    f"♪  {track_name}\n"
                    f"    {artist_names}"
                )

                list_item = QListWidgetItem(text)
                list_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                list_item.setData(Qt.UserRole, track.get("uri")) # Save Spotify URI for playback

                self.track_list.addItem(list_item)

                displayed_tracks += 1

            # Switch from playlists to tracks
            self.playlist_list.setVisible(False)
            self.track_list.setVisible(True)
            self.back_button.setVisible(True)

            self.status.setText(f"{displayed_tracks} tracks loaded")

        except PermissionError as error:

            print("Playlist permission error: ", error)
            self.status.setText("This playlist can't be read by Luma Desk.")
        
        except Exception as error:

            print("Track loading error:", repr(error))
            self.status.setText("Could not load playlist.")

    # Back to playlists
    def show_playlists(self):

        self.track_list.clear()
        self.track_list.setVisible(False)
        self.back_button.setVisible(False)
        self.playlist_list.setVisible(True)
        self.status.setText("Choose a playlist")

    # Track selection
    def track_clicked(self, item):

        track_uri = item.data(Qt.UserRole)

        if not track_uri:
            return

        print("Selected track: ", track_uri)

        try: 

            device = self.spotify.get_active_device()

            if not device:
                self.status.setText("Open Spotify on device first.")
                return

            self.spotify.play_track(track_uri, device.get("id"))

            self.play_pause_button.setText("⏸")

            self.status.setText(f"Playing on {device.get('name', 'Spotify')}")

        except Exception as error:

            print("Playback error: ", repr(error))
            self.status.setText("Could not start playback.")

    def toggle_playback(self):

        try: 

            playback = (self.spotify.get_current_playback())

            if not playback:
                self.status.setText("Nothing is currently playing.")
                return

            is_playing = playback.get("is_playing", False)

            if is_playing:
                self.spotify.pause()
                self.play_pause_button.setText("▶")

                self.status.setText("Paused")

            else:
                self.spotify.resume()
                self.play_pause_button.setText("⏸")
                self.status.setText("Playing")

        except Exception as error:

            print("Playback toggle error:", repr(error))

            self.status.setText("Could not change playback.")

    def previous_track(self):

        try:
            playback = self.spotify.get_current_playback()

            if not playback:
                self.status.setText("Nothing is currently playing.")
                return

            device = playback.get("device")

            if not device:
                self.status.setText("No Spotify device is active.")
                return

            self.spotify.previous_track(device_id=device.get("id"))

            self.status.setText(f"Previous track on {device.get('name', 'Spotify')}")

        except PermissionError:
            self.status.setText("No previous track available.")

        except Exception as error:

            print("Previous track error:", repr(error))

            self.status.setText("Could not go to previous track.")

    def next_track(self):

        try:

            playback = self.spotify.get_current_playback()

            if not playback:
                self.status.setText("Nothing is currently playing.")
                return

            device = playback.get("device")

            if not device:
                self.status.setText("No Spotify device is active.")
                return

            self.spotify.next_track(device_id=device.get("id"))

            self.status.setText(f"Next track on {device.get('name', 'Spotify')}")

        except Exception as error:

            print("Next track error:", repr(error))

            self.status.setText("Could not skip track.")


    def shutdown(self):
        if self.callback_server:
            print("Stopping Spotify callback server...")
            self.callback_server.stop()
            self.callback_server = None

    