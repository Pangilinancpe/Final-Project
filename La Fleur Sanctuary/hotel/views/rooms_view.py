"""
views/rooms_view.py
All rooms in ONE screen. This replaces rooms.py, executive_rooms.py, suites_rooms.py and
presidentials_rooms.py: the 13 rooms now live in data.py, and the tabs below (All / Executive /
Suite / Presidential) replace the three separate windows. Clicking a card opens the room detail;
the Book button goes straight to the booking form.
"""

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config import COLORS, TIER_COLORS
from data import ROOMS, TIERS
from utils import button, clear_layout, fmt_currency, label, load_pixmap, style_badge
from views.base_view import BaseView

COLUMNS, IMG_H = 3, 200


class RoomCard(QFrame):
    """Photo card whose picture fades into the panel colour; highlights on hover."""

    def __init__(self, room: dict, on_details, on_book):
        super().__init__()
        self._pm = load_pixmap(room["image"], TIER_COLORS[room["tier"]])
        self._hot, self._on_details, self._scaled = False, on_details, (0, None)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 130, 18, 16)
        lay.setSpacing(6)
        lay.addWidget(style_badge(QLabel(), room["tier"]), alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(label(room["name"], style="font-size:18px; font-weight:bold;"))
        lay.addWidget(label(f"{fmt_currency(room['pricePerDay'])}<span style='color:{COLORS['muted']}; font-size:11px;'>"
                            f" / day  ·  {fmt_currency(room['pricePerHour'])} / hr</span>",
                            style=f"color:{COLORS['gold']}; font-size:14px;"))
        lay.addWidget(label("AMENITIES & SERVICES", "sectionKicker"))
        for amenity in room["amenities"]:
            lay.addWidget(label(f"<span style='color:{COLORS['gold']};'>✦</span>  {amenity}",
                                style=f"color:{COLORS['tan']};", wrap=True))
        lay.addStretch(1)
        row = QHBoxLayout()
        row.addWidget(button("Details", "ghostButton", lambda _=False: on_details()))
        row.addWidget(button("Book this room", "primaryButton", lambda _=False: on_book()), 1)
        lay.addLayout(row)

    def enterEvent(self, event):
        self._hot = True
        self.update()

    def leaveEvent(self, event):
        self._hot = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_details()

    def paintEvent(self, _):
        w, h = self.width(), self.height()
        if self._scaled[0] != w:  # cache the scaled photo per width
            self._scaled = (w, self._pm.scaled(QSize(w, IMG_H), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                               Qt.TransformationMode.SmoothTransformation))
        s = self._scaled[1]
        p, path = QPainter(self), QPainterPath()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path.addRoundedRect(QRectF(.5, .5, w - 1, h - 1), 10, 10)
        p.setClipPath(path)
        p.fillRect(self.rect(), QColor(COLORS["panel"]))
        p.drawPixmap(0, 0, w, IMG_H, s, (s.width() - w) // 2, (s.height() - IMG_H) // 2, w, IMG_H)
        fade = QLinearGradient(0, 0, 0, IMG_H)
        fade.setColorAt(0, QColor(22, 28, 39, 30))
        fade.setColorAt(1, QColor(22, 28, 39, 255))
        p.fillRect(0, 0, w, IMG_H, QBrush(fade))
        p.setClipping(False)
        p.setPen(QPen(QColor(COLORS["gold"] if self._hot else COLORS["border"]), 1))
        p.drawPath(path)
        p.end()


class RoomsView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = self.make_page()
        outer.setSpacing(12)
        outer.addWidget(label(f"LA FLEUR SANCTUARY  ·  {len(ROOMS)} ROOMS", "sectionKicker"))
        outer.addWidget(label("Our Rooms", "sectionTitle"))

        tabs, group, self._tabs = QHBoxLayout(), QButtonGroup(self), {}
        for tier in ["All"] + [t[0] for t in TIERS]:
            btn = button(tier, "tabButton", lambda _=False, t=tier: self._show(t))
            btn.setCheckable(True)
            group.addButton(btn)
            tabs.addWidget(btn)
            self._tabs[tier] = btn
        tabs.addStretch(1)
        outer.addLayout(tabs)

        self._grid = QGridLayout()
        self._grid.setSpacing(18)
        for c in range(COLUMNS):
            self._grid.setColumnStretch(c, 1)
        col = QVBoxLayout()
        col.addLayout(self._grid)
        col.addStretch(1)
        self.add_scroll(outer, col)

    def on_enter(self, payload: dict) -> None:
        self._show(payload.get("tier_filter", "All"))

    def _show(self, tier: str) -> None:
        self._tabs[tier].setChecked(True)
        clear_layout(self._grid)
        rooms = [r for r in ROOMS if tier == "All" or r["tier"] == tier]
        for i, room in enumerate(rooms):
            card = RoomCard(room, lambda r=room: self.go("room_detail", room=r),
                            lambda r=room: self.go("booking", room=r))
            self._grid.addWidget(card, i // COLUMNS, i % COLUMNS, Qt.AlignmentFlag.AlignTop)
