"""
utils.py — small helpers shared by every view.

  fmt_currency / rgba         formatting
  label / button / divider    one-line widget factories (cut the boilerplate in the views)
  sidebar_card / Stepper      the right-hand "card" and the  − 0 +  control
  error_box / valid_phone     red message box and phone-number check used by the forms
  clear_layout                empty a layout (recursively) before rebuilding it
  load_pixmap / prefetch      pictures: local file in ./images, or a web URL (cached on disk), or a placeholder
  thumb / dummy_qr_pixmap     square thumbnail and the sample (NOT scannable) e-wallet QR picture
  badge_pixmap                small payment logos (GCash, Maya, Visa, ...) drawn with QPainter
"""

import hashlib
import os
import random
import re
import threading
import urllib.error
import urllib.request

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPixmap
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


def error_box():
    """Red message box (hidden at first). Returns (frame, label) — set the label's text, then show the frame."""
    frame = QFrame()
    frame.setObjectName("errorBox")
    lab = label(name="errorText", wrap=True)
    QVBoxLayout(frame).addWidget(lab)
    frame.hide()
    return frame, lab


def valid_phone(text: str) -> bool:
    """Phone number: digits with optional + ( ) - or spaces, 10–12 digits in total (e.g. 0917 123 4567, +63 917 123 4567)."""
    return bool(re.fullmatch(r"\+?[\d\s()-]+", text.strip())) and 10 <= len(re.sub(r"\D", "", text)) <= 12


class Stepper(QFrame):
    """  −  0  +  quantity control. Emits changed(new_qty)."""
    changed = pyqtSignal(int)

    def __init__(self, value: int = 0):
        super().__init__()
        self.setObjectName("transparent")
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


_offline = False  # set after the first network failure so the app doesn't wait on every picture


def _cache_path(url: str) -> str:
    return os.path.join(IMAGE_DIR, "cache", hashlib.md5(url.encode()).hexdigest() + ".jpg")


def _fetch(url: str, timeout: int = 6) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=timeout) as resp:
        return resp.read()


def _from_url(url: str) -> QPixmap:
    """Picture from images/cache (downloaded earlier), else download it once and keep the file."""
    global _offline
    path = _cache_path(url)
    pm = QPixmap(path)
    if pm.isNull() and not _offline:
        try:
            pm.loadFromData(_fetch(url))
            if not pm.isNull():
                os.makedirs(os.path.dirname(path), exist_ok=True)
                pm.save(path)
        except urllib.error.HTTPError:
            pass  # that one picture is missing online; others may still work
        except Exception:
            _offline = True
    return pm


def prefetch_images(urls) -> None:
    """Download missing pictures in a background thread (files only, no Qt) so the screens open instantly."""
    def work():
        for url in urls:
            path = _cache_path(url)
            if os.path.exists(path):
                continue
            try:
                data = _fetch(url)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path + ".part", "wb") as f:
                    f.write(data)
                os.replace(path + ".part", path)
            except urllib.error.HTTPError:
                continue
            except Exception:
                return  # offline: stop trying
    threading.Thread(target=work, daemon=True).start()


def load_pixmap(source: str, accent: str = "#c9a84c", size: QSize = QSize(620, 340), fallback: str = None) -> QPixmap:
    """
    `source` is a web URL or a bare name such as "luxe" (-> images/luxe.jpg|jpeg|png|webp).
    If the local file is missing, `fallback` (a URL) is used. If everything fails, a drawn placeholder is returned,
    so the app never crashes over a picture.
    """
    key = (source, accent)
    if key in _cache:
        return _cache[key]
    pm = QPixmap()
    if source.startswith("http"):
        pm = _from_url(source)
    else:
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            pm = QPixmap(os.path.join(IMAGE_DIR, source + ext))
            if not pm.isNull():
                break
        if pm.isNull() and fallback:
            pm = _from_url(fallback)
    if pm.isNull():
        return _placeholder(size, accent)  # not cached, so a later (online) visit can still find the real picture
    _cache[key] = pm
    return pm


def thumb(pm: QPixmap, size: int) -> QPixmap:
    """Centre-cropped square thumbnail."""
    s = pm.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    return s.copy((s.width() - size) // 2, (s.height() - size) // 2, size, size)


_BRANDS = {"GCash": (QColor(0, 110, 255), "G"), "Maya": (QColor(24, 190, 112), "M")}


def dummy_qr_pixmap(provider: str, amount: str = "", size: int = 220) -> QPixmap:
    """
    A SAMPLE QR picture for the e-wallet screen. It looks like a QR code (corner squares, timing lines, random dots)
    but holds no data, so no phone can scan it. If you have a picture of your own, save it as
    assets/payment/<provider>_qr.png (e.g. gcash_qr.png, maya_qr.png) and it is used instead.
    """
    own = QPixmap(os.path.join(BASE_DIR, "assets", "payment", provider.lower() + "_qr.png"))
    if not own.isNull():
        return own.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    n, quiet = 29, 2                                   # 29 x 29 dots, like a version-3 QR code
    rng = random.Random(provider + amount)
    grid = [[rng.random() < 0.5 for _ in range(n)] for _ in range(n)]
    reserved = [[False] * n for _ in range(n)]

    def stamp(x0, y0, pattern):                        # draw a small fixed pattern and lock those dots
        for dy, row in enumerate(pattern):
            for dx, ch in enumerate(row):
                grid[y0 + dy][x0 + dx], reserved[y0 + dy][x0 + dx] = ch == "#", True

    finder = ["#######", "#.....#", "#.###.#", "#.###.#", "#.###.#", "#.....#", "#######"]
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        for dy in range(-1, 8):                        # white border (separator) around each finder
            for dx in range(-1, 8):
                if 0 <= fx + dx < n and 0 <= fy + dy < n:
                    grid[fy + dy][fx + dx], reserved[fy + dy][fx + dx] = False, True
        stamp(fx, fy, finder)
    stamp(n - 9, n - 9, ["#####", "#...#", "#.#.#", "#...#", "#####"])
    for i in range(8, n - 8):                          # timing lines
        grid[6][i], grid[i][6] = i % 2 == 0, i % 2 == 0

    total = n + quiet * 2
    cell = size / total
    out = QPixmap(size, size)
    out.fill(QColor(255, 255, 255))
    p = QPainter(out)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(20, 24, 36))
    for r in range(n):
        for c in range(n):
            if grid[r][c]:
                p.drawRect(QRectF((c + quiet) * cell, (r + quiet) * cell, cell + 0.4, cell + 0.4))
    color, letter = _BRANDS.get(provider, (QColor(90, 90, 90), provider[:1]))
    mid, badge = size / 2, size * 0.2                  # logo badge in the middle, like real e-wallet QR codes
    p.setBrush(QColor(255, 255, 255))
    p.drawRoundedRect(QRectF(mid - badge / 2 - 3, mid - badge / 2 - 3, badge + 6, badge + 6), 8, 8)
    p.setBrush(color)
    p.drawRoundedRect(QRectF(mid - badge / 2, mid - badge / 2, badge, badge), 7, 7)
    p.setPen(QColor(255, 255, 255))
    p.setFont(QFont("Segoe UI", int(badge * 0.42), QFont.Weight.Bold))
    p.drawText(QRectF(mid - badge / 2, mid - badge / 2, badge, badge), Qt.AlignmentFlag.AlignCenter, letter)
    p.end()
    return out


def badge_pixmap(kind: str, w: int = 46, h: int = 30) -> QPixmap:
    """Small logo tile for a payment option (stylised, drawn in code so no image files are needed)."""
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    box = QRectF(0.5, 0.5, w - 1, h - 1)

    def tile(fill):
        p.setBrush(fill)
        p.drawRoundedRect(box, 4, 4)

    def text(txt, color, pt, weight=QFont.Weight.Bold, rect=None):
        p.setPen(color)
        p.setFont(QFont("Segoe UI", pt, weight))
        p.drawText(rect or box, Qt.AlignmentFlag.AlignCenter, txt)
        p.setPen(Qt.PenStyle.NoPen)

    white = QColor(255, 255, 255)
    if kind == "gcash":
        tile(white)
        p.setBrush(QColor(0, 110, 255))
        p.drawEllipse(QRectF(5, h / 2 - 5, 10, 10))
        text("GCash", QColor(0, 110, 255), 6, rect=QRectF(10, 0, w - 10, h))
    elif kind == "maya":
        tile(QColor(24, 190, 112))
        text("maya", QColor(255, 255, 255), 9)
    elif kind == "visa":
        tile(white)
        text("VISA", QColor(26, 31, 113), 8)
    elif kind == "mastercard":
        tile(white)
        p.setBrush(QColor(235, 0, 27))
        p.drawEllipse(QRectF(w / 2 - 12, h / 2 - 8, 16, 16))
        p.setBrush(QColor(247, 158, 27, 220))
        p.drawEllipse(QRectF(w / 2 - 4, h / 2 - 8, 16, 16))
    elif kind == "discover":
        tile(white)
        text("DISCOVER", QColor(40, 40, 40), 4)
        p.setBrush(QColor(255, 96, 0))
        p.drawEllipse(QRectF(w - 15, h - 11, 9, 9))
    elif kind == "amex":
        tile(QColor(38, 126, 207))
        text("AMEX", QColor(255, 255, 255), 6)
    elif kind == "bank":
        tile(QColor(60, 72, 96))
        p.setBrush(QColor(240, 234, 214))
        p.drawPolygon(*[QPointF(x, y) for x, y in
                        ((w / 2, 5), (w - 9, 12), (9, 12))])
        for i in range(4):
            p.drawRect(QRectF(12 + i * 6, 14, 3, 8))
        p.drawRect(QRectF(10, 24, w - 20, 2))
    else:  # cash
        tile(QColor(70, 140, 90))
        p.setBrush(QColor(236, 244, 226))
        p.drawRoundedRect(QRectF(7, 7, w - 14, h - 14), 3, 3)
        text("₱", QColor(50, 110, 70), 9)
    p.end()
    return pm


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
