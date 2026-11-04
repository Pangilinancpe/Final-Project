
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from config import TIER_COLORS
from utils import FlowLayout, fmt_currency, load_pixmap
from views.base_view import BaseView


class RoomDetailView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._room = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(16)

        back_btn = QPushButton("← Back to rooms")
        back_btn.setObjectName("ghostButton")
        back_btn.clicked.connect(lambda: self.go("rooms"))
        outer.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        row = QHBoxLayout(body)
        row.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(10)

        self._image_label = QLabel()
        self._image_label.setFixedHeight(260)
        self._image_label.setScaledContents(True)
        left.addWidget(self._image_label)

        self._badge = QLabel()
        left.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignLeft)

        self._name_label = QLabel()
        self._name_label.setStyleSheet("font-size:22px; font-weight:600;")
        left.addWidget(self._name_label)

        self._details_label = QLabel()
        self._details_label.setProperty("class", "muted")
        self._details_label.setWordWrap(True)
        left.addWidget(self._details_label)

        amenities_title = QLabel("Room Amenities")
        amenities_title.setStyleSheet("font-weight:600;")
        left.addWidget(amenities_title)

        self._amenities_host = QWidget()
        self._amenities_flow = FlowLayout(self._amenities_host, spacing=8)
        left.addWidget(self._amenities_host)
        left.addStretch(1)

        row.addLayout(left, 2)

        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(8)

        pricing_kicker = QLabel("PRICING")
        pricing_kicker.setProperty("class", "muted")
        sidebar_layout.addWidget(pricing_kicker)

        self._day_price_label = QLabel()
        self._day_price_label.setTextFormat(Qt.TextFormat.RichText)
        sidebar_layout.addWidget(self._day_price_label)

        self._hour_price_label = QLabel()
        self._hour_price_label.setTextFormat(Qt.TextFormat.RichText)
        sidebar_layout.addWidget(self._hour_price_label)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        sidebar_layout.addWidget(divider)

        self._size_label = QLabel()
        sidebar_layout.addWidget(self._size_label)
        self._guests_label = QLabel()
        sidebar_layout.addWidget(self._guests_label)

        book_btn = QPushButton("Book This Room")
        book_btn.setObjectName("primaryButton")
        book_btn.clicked.connect(self._book)
        sidebar_layout.addWidget(book_btn)
        sidebar_layout.addStretch(1)

        row.addWidget(sidebar, 0, Qt.AlignmentFlag.AlignTop)

    def on_enter(self, payload: dict) -> None:
        room = payload.get("room")
        if room is None:
            return
        self._room = room
        color = TIER_COLORS[room["tier"]]

        self._image_label.setPixmap(load_pixmap(room["image"]))
        self._badge.setText(room["tier"])
        self._badge.setStyleSheet(
            f"color:{color}; background-color:{color}1a; border:1px solid {color}55;"
            "border-radius:4px; padding:2px 8px; font-size:11px;"
        )
        self._badge.setFixedWidth(self._badge.sizeHint().width() + 4)
        self._name_label.setText(room["name"])
        self._details_label.setText(room["details"])

        while self._amenities_flow.count():
            item = self._amenities_flow.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for amenity in room["amenities"]:
            chip = QLabel(amenity)
            chip.setObjectName("chipLabel")
            self._amenities_flow.addWidget(chip)

        self._day_price_label.setText(
            f"Per Day &nbsp;&nbsp;<b style='color:#c9a84c; font-size:15px;'>{fmt_currency(room['pricePerDay'])}</b>"
        )
        self._hour_price_label.setText(
            f"Per Hour &nbsp;<b style='color:#b8a98e;'>{fmt_currency(room['pricePerHour'])}</b>"
        )
        self._size_label.setText(f"Size: {room['size']}")
        self._guests_label.setText(f"Max Guests: {room['maxGuests']} pax")

    def _book(self) -> None:
        if self._room:
            self.go("booking", room=self._room)
