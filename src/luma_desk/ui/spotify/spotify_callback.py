from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from PySide6.QtCore import QThread, Signal


class SpotifyCallbackServer(QThread):

    callback_received = Signal(str, str)
    callback_error = Signal(str)

    def __init__(self, port=8888):
        super().__init__()

        self.port = port
        self.server = None

    def run(self):

        callback_server = self

        class CallbackHandler(BaseHTTPRequestHandler):

            def do_GET(self):

                parsed = urlparse(self.path)

                if parsed.path != "/callback":
                    self.send_response(404)
                    self.end_headers()
                    return

                query = parse_qs(parsed.query)

                code = query.get("code", [None])[0]
                state = query.get("state", [None])[0]
                error = query.get("error", [None])[0]

                if error:

                    callback_server.callback_error.emit(error)

                    message = "Spotify login was cancelled or failed."

                elif code:
                    
                    callback_server.callback_received.emit(
                        code,
                        state or "",
                    )

                    message = (
                        "Spotify connected successfully."
                        "<br>You can close this window."
                    )

                else:

                    callback_server.callback_error.emit("No authorization code received.")

                    message = "Spotify authorization failed."

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Luma Desk</title>
                </head>
                <body>
                    <h2>{message}</h2>
                </body>
                </html>
                """

                body = html.encode("utf-8")

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )
                self.send_header(
                    "Content-Length",
                    str(len(body))
                )
                self.end_headers()

                self.wfile.write(body)

                callback_server.server.shutdown()

            def log_message(self, format, *args):
                pass

        self.server = HTTPServer(
            ("127.0.0.1", self.port),
            CallbackHandler,
        )

        self.server.serve_forever()