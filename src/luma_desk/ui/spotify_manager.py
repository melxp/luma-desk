import base64
import hashlib
import secrets
import urllib.parse

import requests

class SpotifyManager:

    CLIENT_ID = "9237f18d4a4c405fbe8dc8d289d27657"

    REDIRECT_URI = "http://127.0.0.1:8888/callback"

    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    API_BASE = "https://api.spotify.com/v1"

    SCOPES = [
        "streaming",
        "user-read-email",
        "user-read-private",
        "user-read-playback-state",
        "user-modify-playback-state",
        "playlist-read-private",
        "playlist-read-collaborative",
    ]

    def __init__(self):
        self.access_token = None
        self.refresh_token = None

        self.code_verifier = None
        self.state = None

    def create_pkce_pair(self):

        # Create a random secret that exists only for this login attempt
        self.code_verifier = secrets.token_urlsafe(64)

        # Create PKCE challenge
        digest = hashlib.sha256(
            self.code_verifier.encode("utf-8")
        ).digest()

        code_challenge = base64.urlsafe_b64encode(
            digest
        ).decode("utf-8").rstrip("=")

        return code_challenge

    def create_authorization_url(self):

        self.state = secrets.token_urlsafe(32)

        code_challenge = self.create_pkce_pair()

        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": " ".join(self.SCOPES),
            "state": self.state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
        }

        return (
            self.AUTH_URL
            + "?"
            + urllib.parse.urlencode(params)
        )

    def exchange_code(self, code):

        if not self.code_verifier:
            raise RuntimeError(
                "PKCE code verifier is missing."
            )

        response = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": self.CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.REDIRECT_URI,
                "code_verifier": self.code_verifier,
            },
            timeout=15,
        )

        response.raise_for_status()

        token_data = response.json()

        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")

        print(
            "Spotify token scopes:",
            token_data.get("scope")
        )

        return token_data


    def _headers(self):
        if not self.access_token:
            raise RuntimeError(
                "Spotify is not connected."
            )

        return {
            "Authorization": (
                f"Bearer {self.access_token}"
            )
        }

  
    def get_playlists(self):

        response = requests.get(
            f"{self.API_BASE}/me/playlists",
            headers=self._headers(),
            params={
                "limit": 50,
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def get_playlist_items(self, playlist_id):

        response = requests.get(
            # This used to point at "/items", which isn't a real
            # Spotify endpoint and returned a 404 every time.
            f"{self.API_BASE}/playlists/{playlist_id}/tracks",
            headers=self._headers(),
            params={
                "limit": 50,
                # "market": "from_token" is deprecated. Leaving the
                # market out lets Spotify use the market tied to
                # the access token instead.
            },
            timeout=15,
        )

        if response.status_code == 403:
            raise PermissionError(
                "Spotify does not allow this playlist "
                "to be read."
            )

        response.raise_for_status()

        return response.json()


    def get_devices(self):

        response = requests.get(
            f"{self.API_BASE}/me/player/devices",
            headers=self._headers(),
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def get_active_device(self):

        data = self.get_devices()

        devices = data.get(
            "devices",
            []
        )

        for device in devices:
            if (
                device.get("is_active")
                and not device.get("is_restricted")
            ):
                return device

        return None

  
    def play_track(
        self,
        track_uri,
        device_id=None,
    ):

        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.put(
            f"{self.API_BASE}/me/player/play",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
            },
            params=params,
            json={
                "uris": [track_uri],
            },
            timeout=15,
        )

        response.raise_for_status()

    def play_playlist_from_position(self, playlist_id, position, device_id=None):
        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.put(
            f"{self.API_BASE}/me/player/play",
            headers={
                **self._headers(),
                "Content-Type": "application/json",
            },
            params=params,
            json={
                "context_uri": (
                    f"spotify:playlist:{playlist_id}"
                ),
                "offset": {
                    "position": position
                },
            },
            timeout=15,
        )

        response.raise_for_status()


    def pause(self, device_id=None):

        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.put(
            f"{self.API_BASE}/me/player/pause",
            headers=self._headers(),
            params=params,
            timeout=15,
        )

        response.raise_for_status()

    def resume(self, device_id=None):

        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.put(
            f"{self.API_BASE}/me/player/play",
            headers=self._headers(),
            params=params,
            timeout=15,
        )

        response.raise_for_status()

    def next_track(self, device_id=None):

        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.post(
            f"{self.API_BASE}/me/player/next",
            headers=self._headers(),
            params=params,
            timeout=15,
        )

        print(
            "Spotify next response:",
            response.status_code,
            response.text
        )

        if response.status_code == 403:
            raise PermissionError(
                "Spotify refused the next-track command."
            )

        response.raise_for_status()


    def previous_track(self, device_id=None):

        params = {}

        if device_id:
            params["device_id"] = device_id

        response = requests.post(
            f"{self.API_BASE}/me/player/previous",
            headers=self._headers(),
            params=params,
            timeout=15,
        )

        print(
            "Spotify previous response:",
            response.status_code,
            response.text
        )

        if response.status_code == 403:
            raise PermissionError(
                "Spotify refused the previous-track command."
            )

        response.raise_for_status()


    def get_current_playback(self):

        response = requests.get(
            f"{self.API_BASE}/me/player",
            headers=self._headers(),
            timeout=15,
        )

        if response.status_code == 204:
            return None

        response.raise_for_status()

        return response.json()