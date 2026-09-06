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

    SCOPES = [
        "streaming",
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
            raise RuntimeError("PKCE code verifier is missing.")

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

        return token_data


    def get_playlists(self):
        if not self.access_token:
            raise RuntimeError("Spotify is not connected.")

        response = requests.get(
            "https://api.spotify.com/v1/me/playlists",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            params={
                "limit": 50,
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def get_playlist_items(self, playlist_id):
        if not self.access_token:
            raise RuntimeError("Spotify is not connected.")

        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            params={
                "limit": 50,
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()