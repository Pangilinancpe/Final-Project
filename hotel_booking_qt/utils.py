"""
utils.py
Small stateless helpers used across views:

  - fmt_currency(n): peso formatting shared by every screen that shows money
  - load_pixmap(url): downloads a room/dish image into a QPixmap, caches it
    by URL for the app's lifetime, and falls back to a solid placeholder
    instead of raising if the network request fails
  - FlowLayout: a Qt layout that wraps children onto new rows as needed —
    used for the amenity "chips" on the room detail view, since Qt has no
    built-in equivalent of CSS flex-wrap
"""

import urllib.request

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QLayout


def fmt_currency(n: float) -> str:
    """Format a peso amount, e.g. fmt_currency(12500) -> '₱12,500'."""
    return "₱" + f"{n:,.0f}"


_pixmap_cache: dict = {}


def load_pixmap(url: str, fallback_size: QSize = None) -> QPixmap:
    """
    Download an image and return it as a QPixmap, caching by URL so the same
    room image isn't re-downloaded for the grid, the detail view, and the
    booking summary sidebar. On any failure (no network, bad URL, etc.),
    returns a solid dark placeholder instead of raising, so the UI stays
    usable offline.
    """
    if fallback_size is None:
        fallback_size = QSize(800, 500)

    if url in _pixmap_cache:
        return _pixmap_cache[url]

    pixmap = QPixmap()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=6) as response:
            raw = response.read()
        pixmap.loadFromData(raw)
    except Exception:
        pixmap = QPixmap()

    if pixmap.isNull():
        pixmap = QPixmap(fallback_size)
        pixmap.fill(QColor("#1a2030"))

    _pixmap_cache[url] = pixmap
    return pixmap


class FlowLayout(QLayout):
    """
    Wraps child widgets onto new rows once the current row runs out of
    horizontal space. Adapted from Qt's standard "Flow Layout" example.
    Used by RoomDetailView for the amenity chip list.
    """

    def __init__(self, parent=None, margin: int = 0, spacing: int = 6):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x, y = rect.x(), rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + hint.width() + spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y()
