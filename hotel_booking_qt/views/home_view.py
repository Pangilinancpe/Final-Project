"""
views/home_view.py
Landing / hero screen: banner image with an overlaid headline, the three
tier teaser cards, and the stats strip. Equivalent of the React <HomeView/>.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from config import COLORS, TIER_COLORS
from data import ROOMS
from utils import fmt_currency, load_pixmap
from views.base_view import BaseView

_TIERS = [
    ("Premium", "Premium Rooms", "Our finest suites with panoramic views, jacuzzis, and butler service."),
    ("Deluxe", "Deluxe Rooms", "Spacious and elegantly appointed for families and discerning guests."),
    ("Economy", "Economy Rooms", "Clean, comfortable, and affordable — everything you need."),
]

_STATS = [
    ("3 Tiers", "Room Types"),
    ("Per Day / Hour", "Pricing"),
    ("Senior & Child", "Family Discount"),
    ("24/7 Dining", "Room Service"),
]

_HERO_IMAGE = "https://images.unsplash.com/photo-1677129667171-92abd8740fa3?w=1400&h=600&fit=crop&auto=format"


class _HeroBanner(QWidget):
    """Background image with a dark-tinted overlay holding the hero copy."""

    def __init__(self, on_browse, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(360)

        self._image_label = QLabel(self)
        self._image_label.setScaledContents(True)
        self._image_label.setPixmap(load_pixmap(_HERO_IMAGE))

        self._overlay = QWidget(self)
        self._overlay.setStyleSheet("background-color: rgba(13, 17, 23, 170);")
        overlay_layout = QVBoxLayout(self._overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setSpacing(10)

        kicker = QLabel("MANILA · EST. 2001")
        kicker.setObjectName("heroKicker")
        kicker.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Your Home Away\nFrom Home")
        title.setObjectName("heroTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(
            "Premium, Deluxe, and Economy rooms — priced per day or per hour.\n"
            "Family-friendly with senior & child discounts."
        )
        subtitle.setObjectName("heroSub")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        browse_btn = QPushButton("Browse Available Rooms")
        browse_btn.setObjectName("primaryButton")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(on_browse)

        overlay_layout.addWidget(kicker)
        overlay_layout.addWidget(title)
        overlay_layout.addWidget(subtitle)
        overlay_layout.addSpacing(6)
        overlay_layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        self._image_label.setGeometry(self.rect())
        self._overlay.setGeometry(self.rect())
        super().resizeEvent(event)


class HomeView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        body_layout.addWidget(_HeroBanner(on_browse=lambda: self.go("rooms")))

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 36, 48, 36)
        content_layout.setSpacing(26)
        body_layout.addWidget(content)

        tiers_row = QHBoxLayout()
        tiers_row.setSpacing(18)
        for tier, label, desc in _TIERS:
            tiers_row.addWidget(self._tier_card(tier, label, desc))
        content_layout.addLayout(tiers_row)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {COLORS['border']};")
        content_layout.addWidget(divider)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(18)
        for value, label in _STATS:
            stats_row.addWidget(self._stat_block(value, label))
        content_layout.addLayout(stats_row)

    def _tier_card(self, tier: str, label: str, desc: str) -> QFrame:
        color = TIER_COLORS[tier]
        cheapest = min(r["pricePerDay"] for r in ROOMS if r["tier"] == tier)

        card = QFrame()
        card.setObjectName("card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)

        badge = QLabel(tier)
        badge.setStyleSheet(
            f"color:{color}; background-color:{color}1a; border:1px solid {color}55;"
            "border-radius:4px; padding:2px 8px; font-size:11px;"
        )
        badge.setFixedWidth(badge.sizeHint().width() + 4)

        title = QLabel(label)
        title.setStyleSheet("font-size:15px; font-weight:600;")

        desc_label = QLabel(desc)
        desc_label.setProperty("class", "muted")
        desc_label.setWordWrap(True)

        price_label = QLabel(
            f"From <span style='color:{color}; font-weight:600;'>{fmt_currency(cheapest)}</span>/night"
        )
        price_label.setProperty("class", "muted")
        price_label.setTextFormat(Qt.TextFormat.RichText)

        layout.addWidget(badge)
        layout.addWidget(title)
        layout.addWidget(desc_label)
        layout.addWidget(price_label)

        def _handle_click(_event, t=tier):
            self.go("rooms", tier_filter=t)

        card.mousePressEvent = _handle_click
        return card

    def _stat_block(self, value: str, label: str) -> QWidget:
        block = QWidget()
        layout = QVBoxLayout(block)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(2)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color:{COLORS['gold']}; font-size:15px; font-weight:600;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        caption_label = QLabel(label)
        caption_label.setProperty("class", "muted")
        caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(caption_label)
        return block
