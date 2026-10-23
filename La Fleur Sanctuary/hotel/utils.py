"""
utils.py — small helpers shared by every view.

  fmt_currency / rgba         formatting
  label / button / divider    one-line widget factories (cut the boilerplate in the views)
  sidebar_card / Stepper      the right-hand "card" and the  − 0 +  control
  clear_layout                empty a layout (recursively) before rebuilding it
  load_pixmap                 room/hero image: local file in ./images, or a URL, or a drawn placeholder
"""

import hashlib
import os
import urllib.request

from PyQt6.QtCore import QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from config import SERVICE_IMAGES_URL, TIER_COLORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
SERVICE_DIR = os.path.join(BASE_DIR, "assets", "services")


def fmt_currency(n: float) -> str:
    return f"₱{n:,.0f}"


def rgba(color: str, alpha: int) -> str:
    """'#c9a84c' -> 'rgba(201, 168, 76, alpha)'. (Qt reads 8-digit hex as #AARRGGBB, so never append alpha to hex.)"""
    c = QColor(color)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha})"


def label(text="", name=None, muted=False, style="", wrap=False, align=None) -> QLabel:
    lab = QLabel(text)
    if name:
        lab.setObjectName(name)
    if muted:
        lab.setProperty("class", "muted")
    if style:
        lab.setStyleSheet(style)
    if align is not None:
        lab.setAlignment(align)
    lab.setWordWrap(wrap)
    return lab


def button(text, name, slot=None) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName(name)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if slot:
        btn.clicked.connect(slot)
    return btn


def divider() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFixedHeight(1)
    return line


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget, child = item.widget(), item.layout()  # read once: widget() is None after setParent(None)
        if widget:
            widget.setParent(None)
            widget.deleteLater()
        elif child:
            clear_layout(child)


def sidebar_card(title: str, width: int = 280):
    """Right-hand card with a bold title. Returns (frame, its QVBoxLayout)."""
    card = QFrame()
    card.setObjectName("card")
    card.setFixedWidth(width)
    lay = QVBoxLayout(card)
    lay.addWidget(label(title, style="font-weight:600;"))
    return card, lay


def style_badge(lab: QLabel, tier: str) -> QLabel:
    """Turn a QLabel into a coloured tier pill."""
    color = TIER_COLORS[tier]
    lab.setText(tier)
    lab.setStyleSheet(f"color:{color}; background-color:{rgba(color, 26)}; border:1px solid {rgba(color, 85)};"
                      "border-radius:4px; padding:2px 8px; font-size:11px;")
    lab.setFixedWidth(lab.fontMetrics().horizontalAdvance(tier) + 28)
    return lab


class Stepper(QFrame):
    """  −  0  +  quantity control. Emits changed(new_qty)."""
    changed = pyqtSignal(int)

    def __init__(self, value: int = 0):
        super().__init__()
        self.setObjectName("stepper")
        self.value = value
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._label = label(str(value), align=Qt.AlignmentFlag.AlignCenter)
        self._label.setFixedWidth(24)
        lay.addWidget(button("−", "qtyButton", lambda _=False: self.set(self.value - 1)))
        lay.addWidget(self._label)
        lay.addWidget(button("+", "qtyButton", lambda _=False: self.set(self.value + 1)))

    def set(self, n: int, emit: bool = True) -> None:
        self.value = max(0, n)
        self._label.setText(str(self.value))
        if emit:
            self.changed.emit(self.value)


_cache: dict = {}


def _placeholder(size: QSize, accent: str) -> QPixmap:
    pm, c = QPixmap(size), QColor(accent)
    w, h = size.width(), size.height()
    p, g = QPainter(pm), QLinearGradient(0, 0, 0, h)
    g.setColorAt(0, QColor("#1b2236"))
    g.setColorAt(1, c.darker(300))
    p.fillRect(pm.rect(), QBrush(g))
    p.setPen(Qt.PenStyle.NoPen)
    for col, x, y, bw, bh in [(QColor(255, 235, 190, 80), .62, .11, .28, .42), (c.darker(130), .12, .52, .55, .26),
                              (QColor("#f2f4f8"), .15, .46, .16, .10), (c, .12, .62, .55, .16)]:
        p.setBrush(col)
        p.drawRoundedRect(int(w * x), int(h * y), int(w * bw), int(h * bh), 5, 5)
    p.end()
    return pm


def load_pixmap(source: str, accent: str = "#c9a84c", size: QSize = QSize(620, 340)) -> QPixmap:
    """
    `source` is an http(s) URL or a bare name such as "luxe" (-> images/luxe.jpg|jpeg|png|webp).
    Anything missing/offline falls back to a drawn placeholder, so the app never crashes over an image.
    """
    key = (source, accent)
    if key not in _cache:
        pm = QPixmap()
        if source.startswith("http"):  # downloaded once, then reused from images/cache
            cached = os.path.join(IMAGE_DIR, "cache", hashlib.md5(source.encode()).hexdigest() + ".jpg")
            pm = QPixmap(cached)
            if pm.isNull():
                try:
                    req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        pm.loadFromData(resp.read())
                    if not pm.isNull():
                        os.makedirs(os.path.dirname(cached), exist_ok=True)
                        pm.save(cached)
                except Exception:
                    pass
        else:
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                pm = QPixmap(os.path.join(IMAGE_DIR, source + ext))
                if not pm.isNull():
                    break
        _cache[key] = pm if not pm.isNull() else _placeholder(size, accent)
    return _cache[key]


def load_service_image(filename: str) -> QPixmap:
    """assets/services/<filename>; if missing, download it from the GitHub repo once and keep a local copy."""
    key = ("service", filename)
    if key not in _cache:
        path = os.path.join(SERVICE_DIR, filename)
        pm = QPixmap(path)
        if pm.isNull():
            try:
                with urllib.request.urlopen(urllib.request.Request(SERVICE_IMAGES_URL + filename, headers={"User-Agent": "Mozilla/5.0"}), timeout=8) as resp:
                    raw = resp.read()
                pm.loadFromData(raw)
                if not pm.isNull():
                    os.makedirs(SERVICE_DIR, exist_ok=True)
                    pm.save(path)
            except Exception:
                pass
        _cache[key] = pm if not pm.isNull() else _placeholder(QSize(620, 340), "#c9a84c")
    return _cache[key]


class CoverImage(QWidget):
    """Fixed-height picture that fills its width and crops the overflow (no stretching), with rounded corners."""

    def __init__(self, height: int):
        super().__init__()
        self.setFixedHeight(height)
        self._pm = None

    def set_pixmap(self, pm: QPixmap) -> None:
        self._pm = pm
        self.update()

    def paintEvent(self, _):
        if self._pm is None:
            return
        w, h = self.width(), self.height()
        s = self._pm.scaled(QSize(w, h), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        p, path = QPainter(self), QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), 8, 8)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setClipPath(path)
        p.drawPixmap(0, 0, w, h, s, (s.width() - w) // 2, (s.height() - h) // 2, w, h)
        p.end()
