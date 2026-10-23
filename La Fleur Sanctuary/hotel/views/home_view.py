"""views/home_view.py — landing screen: hero banner, tier teaser cards, stats strip."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config import COLORS, TIER_COLORS
from data import ROOMS, TIERS
from utils import button, divider, fmt_currency, label, load_pixmap, style_badge
from views.base_view import BaseView

CENTER = Qt.AlignmentFlag.AlignCenter
_HERO_IMAGE = "https://images.unsplash.com/photo-1677129667171-92abd8740fa3?w=1400&h=600&fit=crop&auto=format"

_STATS = [
    ("3 Tiers", "Room Types"),
    (f"{len(ROOMS)} Rooms", "Handpicked"),
    ("Senior & Child", "Family Discount"),
    ("24/7 Dining", "Room Service"),
]


class _HeroBanner(QWidget):
    """Background image with a dark overlay holding the hero copy."""

    def __init__(self, on_browse, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(360)
        self._image = QLabel(self)
        self._image.setScaledContents(True)
        self._image.setPixmap(load_pixmap(_HERO_IMAGE, COLORS["gold"], QSize(1400, 600)))

        self._overlay = QFrame(self)
        self._overlay.setObjectName("overlay")
        lay = QVBoxLayout(self._overlay)
        lay.setAlignment(CENTER)
        lay.setSpacing(10)
        lay.addWidget(label("MANILA · EST. 2001", "heroKicker", align=CENTER))
        lay.addWidget(label("Your Home Away\nFrom Home", "heroTitle", align=CENTER))
        lay.addWidget(label("Executive, Suite, and Presidential rooms — priced per day or per hour.\n"
                            "Family-friendly with senior & child discounts.", "heroSub", wrap=True, align=CENTER))
        lay.addSpacing(6)
        lay.addWidget(button("Browse Available Rooms", "primaryButton", on_browse), alignment=CENTER)

    def resizeEvent(self, event):
        self._image.setGeometry(self.rect())
        self._overlay.setGeometry(self.rect())
        super().resizeEvent(event)


class HomeView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = self.make_page(margins=(0, 0, 0, 0))

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(_HeroBanner(lambda: self.go("rooms")))

        content = QVBoxLayout()
        content.setContentsMargins(48, 36, 48, 36)
        content.setSpacing(26)
        tiers = QHBoxLayout()
        tiers.setSpacing(18)
        for tier, title, desc in TIERS:
            tiers.addWidget(self._tier_card(tier, title, desc))
        stats = QHBoxLayout()
        for value, caption in _STATS:
            stats.addLayout(self._stat(value, caption))
        content.addLayout(tiers)
        content.addWidget(divider())
        content.addLayout(stats)

        body.addLayout(content)
        body.addStretch(1)
        self.add_scroll(outer, body)

    def _tier_card(self, tier: str, title: str, desc: str) -> QFrame:
        color = TIER_COLORS[tier]
        cheapest = min(r["pricePerDay"] for r in ROOMS if r["tier"] == tier)
        card = QFrame()
        card.setObjectName("card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(6)
        lay.addWidget(style_badge(QLabel(), tier), alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(label(title, style="font-size:15px; font-weight:600;"))
        lay.addWidget(label(desc, muted=True, wrap=True))
        lay.addWidget(label(f"From <span style='color:{color}; font-weight:600;'>{fmt_currency(cheapest)}</span> / night", muted=True))
        card.mousePressEvent = lambda _e, t=tier: self.go("rooms", tier_filter=t)
        return card

    @staticmethod
    def _stat(value: str, caption: str) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(2)
        lay.addWidget(label(value, style=f"color:{COLORS['gold']}; font-size:15px; font-weight:600;", align=CENTER))
        lay.addWidget(label(caption, muted=True, align=CENTER))
        return lay
