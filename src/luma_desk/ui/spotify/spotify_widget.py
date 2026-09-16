import json
import webbrowser

from PySide6.QtCore import QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QFontMetrics, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem
)

from luma_desk.ui.spotify_manager import SpotifyManager
from luma_desk.ui.spotify.spotify_callback import SpotifyCallbackServer
from luma_desk.ui.spotify.player_icons import make_icon, rounded_pixmap


class SpotifyWidget(QFrame):

    ICON_COLOUR = QColor(255, 255, 255, 235)
    ACCENT_ICON_COLOUR = QColor(45, 55, 35, 255)

    def __init__(self):
        super().__init__()

        # Spotify manager
        self.spotify = SpotifyManager()
        self.callback_server = None
        self.current_playlist_id = None

        # Playback state, kept up to date by the poll timer
        self.device_id = None
        self.is_playing = False
        self.progress_ms = 0
        self.duration_ms = 0
        self.art_url = None

        self.network = QNetworkAccessManager(self)

        # Widget styling
        self.setFixedWidth(280)
        self.setMinimumHeight(430)

        self.setStyleSheet("""
            QFrame#spotify {
                background-color: rgba(82, 96, 68, 210);
                border-radius: 12px;
            }

            QFrame#nowPlaying {
                background: rgba(0, 0, 0, 60);
                border-radius: 10px;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QLabel#trackLabel {
                color: white;
                font-family: "Nunito Sans";
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#artistLabel {
                color: rgba(255, 255, 255, 150);
                font-family: "Nunito Sans";
                font-size: 11px;
            }

            QLabel#timeLabel {
                color: rgba(255, 255, 255, 130);
                font-family: "Nunito Sans";
                font-size: 10px;
            }

            QLabel#statusLabel {
                color: rgba(255, 255, 255, 140);
                font-family: "Nunito Sans";
                font-size: 11px;
            }

            QProgressBar {
                background: rgba(255, 255, 255, 40);
                border: none;
                border-radius: 2px;
                height: 4px;
            }

            QProgressBar::chunk {
                background: rgba(232, 213, 177, 230);
                border-radius: 2px;
            }

            QPushButton {
                color: white;
                background: rgba(255, 255, 255, 45);
                border: none;
                border-radius: 8px;
                font-family: "Nunito Sans";
                font-size: 11px;
                padding: 7px;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 75);
            }

            QPushButton:pressed {
                background: rgba(255, 255, 255, 100);
            }

            QPushButton:disabled {
                background: rgba(255, 255, 255, 15);
            }

            QPushButton#playButton {
                background: rgba(232, 213, 177, 200);
                border-radius: 19px;
            }

            QPushButton#playButton:hover {
                background: rgba(232, 213, 177, 240);
            }

            QPushButton#playButton:disabled {
                background: rgba(232, 213, 177, 60);
            }

            QPushButton#stepButton {
                background: transparent;
                border-radius: 16px;
            }

            QPushButton#stepButton:hover {
                background: rgba(255, 255, 255, 45);
            }

            QListWidget {
                color: white;
                background: rgba(0, 0, 0, 60);
                border: none;
                border-radius: 10px;
                font-family: "Nunito Sans";
                font-size: 11px;
                outline: none;
                padding: 4px;
            }

            QListWidget::item {
                color: white;
                background: transparent;
                border-radius: 6px;
                padding: 6px;
            }

            QListWidget::item:hover {
                background: rgba(255, 255, 255, 25);
            }

            QListWidget::item:selected {
                color: white;
                background: rgba(232, 213, 177, 60);
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 4px 2px 4px 0px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 70);
                border-radius: 3px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        self.setObjectName("spotify")

        # Now playing panel
        self.art_label = QLabel()
        self.art_label.setFixedSize(52, 52)
        self.art_label.setAlignment(Qt.AlignCenter)
        self.clear_album_art()

        self.track_label = QLabel("Nothing playing")
        self.track_label.setObjectName("trackLabel")

        self.artist_label = QLabel("Connect to get started")
        self.artist_label.setObjectName("artistLabel")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)

        self.elapsed_label = QLabel("0:00")
        self.elapsed_label.setObjectName("timeLabel")

        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("timeLabel")

        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(4)

        time_row.addWidget(self.elapsed_label)
        time_row.addStretch()
        time_row.addWidget(self.duration_label)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        text_column.addWidget(self.track_label)
        text_column.addWidget(self.artist_label)
        text_column.addWidget(self.progress_bar)
        text_column.addLayout(time_row)

        now_playing_layout = QHBoxLayout()
        now_playing_layout.setContentsMargins(10, 10, 10, 10)
        now_playing_layout.setSpacing(10)

        now_playing_layout.addWidget(self.art_label)
        now_playing_layout.addLayout(text_column)

        self.now_playing = QFrame()
        self.now_playing.setObjectName("nowPlaying")
        self.now_playing.setLayout(now_playing_layout)

        # Playback buttons
        self.previous_button = QPushButton()
        self.previous_button.setObjectName("stepButton")
        self.previous_button.setFixedSize(32, 32)
        self.previous_button.setIcon(make_icon("previous", self.ICON_COLOUR))
        self.previous_button.setIconSize(QSize(20, 20))
        self.previous_button.clicked.connect(self.previous_track)

        self.play_pause_button = QPushButton()
        self.play_pause_button.setObjectName("playButton")
        self.play_pause_button.setFixedSize(38, 38)
        self.play_pause_button.setIcon(
            make_icon("play", self.ACCENT_ICON_COLOUR)
        )
        self.play_pause_button.setIconSize(QSize(20, 20))
        self.play_pause_button.clicked.connect(self.toggle_playback)

        self.next_button = QPushButton()
        self.next_button.setObjectName("stepButton")
        self.next_button.setFixedSize(32, 32)
        self.next_button.setIcon(make_icon("next", self.ICON_COLOUR))
        self.next_button.setIconSize(QSize(20, 20))
        self.next_button.clicked.connect(self.next_track)

        for button in (
            self.previous_button,
            self.play_pause_button,
            self.next_button,
        ):
            button.setCursor(Qt.PointingHandCursor)
            button.setEnabled(False)

        self.playback_layout = QHBoxLayout()
        self.playback_layout.setContentsMargins(0, 0, 0, 0)
        self.playback_layout.setSpacing(14)

        self.playback_layout.addStretch()
        self.playback_layout.addWidget(self.previous_button)
        self.playback_layout.addWidget(self.play_pause_button)
        self.playback_layout.addWidget(self.next_button)
        self.playback_layout.addStretch()

        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.setVisible(False)
        self.playlist_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlist_list.itemClicked.connect(self.load_playlist_tracks)

        # Track list
        self.track_list = QListWidget()
        self.track_list.setVisible(False)
        self.track_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_list.itemClicked.connect(self.track_clicked)

        # Back button
        self.back_button = QPushButton("‹  All playlists")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setVisible(False)
        self.back_button.clicked.connect(self.show_playlists)

        # Status
        self.status = QLabel("Connect your Spotify account")
        self.status.setObjectName("statusLabel")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)

        # Connect button
        self.connect_button = QPushButton("Connect Spotify")
        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.connect_button.clicked.connect(self.connect_spotify)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(self.now_playing)
        layout.addLayout(self.playback_layout)
        layout.addWidget(self.playlist_list)
        layout.addWidget(self.track_list)
        layout.addWidget(self.back_button)
        layout.addWidget(self.status)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

        # The progress bar moves on its own between polls, so the
        # widget isn't asking Spotify for an update every second.
        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(1000)
        self.tick_timer.timeout.connect(self.tick)

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(3000)
        self.poll_timer.timeout.connect(self.request_playback)

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
            self.status.setText("Choose a playlist")

            self.connect_button.setVisible(False)

            self.enable_playback_controls(True)

            # Load user's playlists
            self.load_playlists()

            self.request_playback()
            self.poll_timer.start()
            self.tick_timer.start()

        except Exception as error:

            print("Spotify token error: ", repr(error))
            self.spotify_error("token_exchange_failed")

    def spotify_error(self, error):

        print("Spotify authorization error: ", error)
        self.status.setText("Spotify connection failed.")
        self.connect_button.setEnabled(True)
        self.connect_button.setVisible(True)
        self.enable_playback_controls(False)

    def enable_playback_controls(self, enabled):

        self.previous_button.setEnabled(enabled)
        self.play_pause_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)


    # Playlists
    def elide(self, text, width):
        metrics = QFontMetrics(self.playlist_list.font())

        return metrics.elidedText(text, Qt.ElideRight, width)

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

                total = playlist.get("tracks", {}).get("total", 0)

                item = QListWidgetItem(
                    f"{self.elide(name, 170)}\n{total} tracks"
                )

                item.setData(Qt.UserRole, playlist_id)

                self.playlist_list.addItem(item)

            self.playlist_list.setVisible(True)
            self.track_list.setVisible(False)
            self.back_button.setVisible(False)

            self.status.setText(f"{len(playlists)} playlists")

        except Exception as error:

            print("Playlist loading error:", repr(error))

            self.status.setText("Could not load playlists.")


    # Playlist tracks
    def load_playlist_tracks(self, item):

        playlist_id = item.data(Qt.UserRole)

        if not playlist_id:
            return

        self.current_playlist_id = playlist_id

        try:

            playlist_data = self.spotify.get_playlist_items(playlist_id)
            
            self.track_list.clear()

            tracks = playlist_data.get("items", [])

            displayed_tracks = 0

            for position, playlist_item in enumerate(tracks):

                track = playlist_item.get("track")

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
                    f"{self.elide(track_name, 190)}\n"
                    f"{self.elide(artist_names, 190)}"
                )

                list_item = QListWidgetItem(text)
                list_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                list_item.setData(Qt.UserRole, track.get("uri")) # Save Spotify URI for playback
                list_item.setData(Qt.UserRole + 1, position)

                self.track_list.addItem(list_item)

                displayed_tracks += 1

            # Switch from playlists to tracks
            self.playlist_list.setVisible(False)
            self.track_list.setVisible(True)
            self.back_button.setVisible(True)

            self.status.setText(f"{displayed_tracks} tracks")

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

        track_position = item.data(Qt.UserRole + 1)

        if not track_uri:
            return

        if self.current_playlist_id is None:
            self.status.setText("No playlist selected.")
            return

        if track_position is None:
            self.status.setText("Track position unavailable.")
            return

        try: 

            device = self.spotify.get_active_device()

            if not device:
                self.status.setText(
                    "Open Spotify on your phone or desktop first."
                )
                return

            self.device_id = device.get("id")

            self.spotify.play_playlist_from_position(
                self.current_playlist_id,
                track_position,
                self.device_id,
            )

            self.set_playing(True)
            self.status.setText(f"Playing on {device.get('name', 'Spotify')}")

            # Give Spotify a moment, then pick up the new track.
            QTimer.singleShot(700, self.request_playback)

        except Exception as error:

            print("Playback error: ", repr(error))
            self.status.setText("Could not start playback.")

    # Playback controls
    def set_playing(self, playing):
        self.is_playing = playing

        self.play_pause_button.setIcon(
            make_icon(
                "pause" if playing else "play",
                self.ACCENT_ICON_COLOUR,
            )
        )

    def toggle_playback(self):

        try:

            if self.is_playing:
                self.spotify.pause(self.device_id)
                self.set_playing(False)
                self.status.setText("Paused")

            else:
                self.spotify.resume(self.device_id)
                self.set_playing(True)
                self.status.setText("Playing")

        except Exception as error:

            print("Playback toggle error:", repr(error))

            self.status.setText("Could not change playback.")

        QTimer.singleShot(700, self.request_playback)

    def previous_track(self):

        try:
            self.spotify.previous_track(device_id=self.device_id)

        except PermissionError:
            self.status.setText("No previous track available.")

        except Exception as error:

            print("Previous track error:", repr(error))

            self.status.setText("Could not go to previous track.")

        QTimer.singleShot(700, self.request_playback)

    def next_track(self):

        try:
            self.spotify.next_track(device_id=self.device_id)

        except PermissionError:
            self.status.setText("Spotify refused that (Premium only).")

        except Exception as error:

            print("Next track error:", repr(error))

            self.status.setText("Could not skip track.")

        QTimer.singleShot(700, self.request_playback)

    # Now playing
    def format_time(self, milliseconds):
        total_seconds = max(0, milliseconds // 1000)

        return f"{total_seconds // 60}:{total_seconds % 60:02d}"

    def tick(self):
        # Move the bar along between the real updates.
        if self.is_playing and self.duration_ms:
            self.progress_ms = min(
                self.progress_ms + 1000,
                self.duration_ms,
            )

        self.update_progress()

    def update_progress(self):
        if not self.duration_ms:
            self.progress_bar.setValue(0)
            self.elapsed_label.setText("0:00")
            self.duration_label.setText("0:00")
            return

        fraction = self.progress_ms / self.duration_ms

        self.progress_bar.setValue(int(fraction * 1000))
        self.elapsed_label.setText(self.format_time(self.progress_ms))
        self.duration_label.setText(self.format_time(self.duration_ms))

    def clear_album_art(self):
        placeholder = QPixmap(52, 52)
        placeholder.fill(QColor(255, 255, 255, 30))

        self.art_label.setPixmap(rounded_pixmap(placeholder, 52))

    # Asking Spotify what's playing, without freezing the window
    def request_playback(self):
        if not self.spotify.access_token:
            return

        request = QNetworkRequest(QUrl(f"{self.spotify.API_BASE}/me/player"))

        request.setRawHeader(
            b"Authorization",
            f"Bearer {self.spotify.access_token}".encode("utf-8"),
        )

        reply = self.network.get(request)
        reply.finished.connect(lambda reply=reply: self.playback_received(reply))

    def playback_received(self, reply):
        status_code = reply.attribute(
            QNetworkRequest.Attribute.HttpStatusCodeAttribute
        )

        body = bytes(reply.readAll())

        reply.deleteLater()

        # 204 means Spotify is connected but idle.
        if status_code == 204 or not body:
            self.show_nothing_playing()
            return

        if status_code != 200:
            return

        try:
            playback = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return

        device = playback.get("device") or {}
        self.device_id = device.get("id", self.device_id)

        self.set_playing(bool(playback.get("is_playing")))

        self.progress_ms = playback.get("progress_ms") or 0

        track = playback.get("item") or {}

        self.duration_ms = track.get("duration_ms") or 0

        self.track_label.setText(
            self.elide(track.get("name", "Nothing playing"), 165)
        )

        artists = ", ".join(
            artist.get("name", "")
            for artist in track.get("artists", [])
        )

        self.artist_label.setText(self.elide(artists, 165))

        self.update_progress()
        self.request_album_art(track)

    def show_nothing_playing(self):
        self.set_playing(False)

        self.progress_ms = 0
        self.duration_ms = 0
        self.art_url = None

        self.track_label.setText("Nothing playing")
        self.artist_label.setText("Pick a track below")

        self.clear_album_art()
        self.update_progress()

    def request_album_art(self, track):
        images = track.get("album", {}).get("images", [])

        if not images:
            return

        # The last image is the smallest one.
        url = images[-1].get("url")

        if not url or url == self.art_url:
            return

        self.art_url = url

        reply = self.network.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(lambda reply=reply: self.art_received(reply))

    def art_received(self, reply):
        body = bytes(reply.readAll())

        reply.deleteLater()

        pixmap = QPixmap()

        if body and pixmap.loadFromData(body):
            self.art_label.setPixmap(rounded_pixmap(pixmap, 52))

    def shutdown(self):
        self.poll_timer.stop()
        self.tick_timer.stop()

        if self.callback_server:
            print("Stopping Spotify callback server...")
            self.callback_server.stop()
            self.callback_server = None