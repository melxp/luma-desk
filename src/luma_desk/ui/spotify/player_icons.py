"""Small playback icons drawn with QPainter.

Characters like ⏮ and ⏭ fall back to whatever the system has, which
on Windows turns into coloured emoji boxes. Drawing them keeps the
controls the right colour and the right size.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QIcon, QPainter, QPixmap, QPolygonF


def triangle(painter, left, top, width, height, pointing_right=True):
    if pointing_right:
        points = [
            QPointF(left, top),
            QPointF(left, top + height),
            QPointF(left + width, top + height / 2),
        ]
    else:
        points = [
            QPointF(left + width, top),
            QPointF(left + width, top + height),
            QPointF(left, top + height / 2),
        ]

    painter.drawPolygon(QPolygonF(points))


def make_pixmap(kind, colour, size):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(colour))

    if kind == "play":
        triangle(painter, size * 0.30, size * 0.20, size * 0.48, size * 0.60)

    elif kind == "pause":
        bar_width = size * 0.13

        painter.drawRoundedRect(
            QRectF(size * 0.31, size * 0.22, bar_width, size * 0.56), 2, 2
        )
        painter.drawRoundedRect(
            QRectF(size * 0.56, size * 0.22, bar_width, size * 0.56), 2, 2
        )

    elif kind == "next":
        triangle(painter, size * 0.20, size * 0.24, size * 0.40, size * 0.52)

        painter.drawRoundedRect(
            QRectF(size * 0.64, size * 0.24, size * 0.10, size * 0.52), 2, 2
        )

    elif kind == "previous":
        triangle(
            painter,
            size * 0.40,
            size * 0.24,
            size * 0.40,
            size * 0.52,
            pointing_right=False,
        )

        painter.drawRoundedRect(
            QRectF(size * 0.26, size * 0.24, size * 0.10, size * 0.52), 2, 2
        )

    painter.end()

    return pixmap


def make_icon(kind, colour, size=22):
    return QIcon(make_pixmap(kind, colour, size))


def rounded_pixmap(pixmap, size, radius=6):
    """Crop album art into a rounded square."""

    scaled = pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )

    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    path_rect = QRectF(0, 0, size, size)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(scaled))
    painter.drawRoundedRect(path_rect, radius, radius)

    painter.end()

    return rounded