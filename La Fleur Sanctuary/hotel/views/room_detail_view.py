from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout

from config import TIER_COLORS
from utils import CoverImage, button, clear_layout, divider, fmt_currency, label, load_pixmap, sidebar_card, style_badge
from views.base_view import BaseView


class RoomDetailView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._room = None
        outer = self.make_page(back=lambda: self.go("rooms"))

        row = QHBoxLayout()
        row.setSpacing(24)
        left = QVBoxLayout()
        left.setSpacing(10)

        self._image = CoverImage(260)
        self._badge = label()
        self._name = label(style="font-size:22px; font-weight:600;")
        self._details = label(muted=True, wrap=True)
        self._chips = QGridLayout()
        self._chips.setSpacing(8)

        left.addWidget(self._image)
        left.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignLeft)
        left.addWidget(self._name)
        left.addWidget(self._details)
        left.addWidget(label("Room Amenities", style="font-weight:600;"))
        left.addLayout(self._chips)
        left.addStretch(1)
        row.addLayout(left, 2)

        card, lay = sidebar_card("PRICING")
        lay.setSpacing(8)
        self._day, self._hour = label(), label()
        self._size, self._guests = label(), label()
        for w in (self._day, self._hour, divider(), self._size, self._guests,
                  button("Book This Room", "primaryButton", self._book)):
            lay.addWidget(w)
        lay.addStretch(1)
        row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self.add_scroll(outer, row)

    def on_enter(self, payload: dict) -> None:
        room = payload.get("room")
        if room is None:
            return
        self._room = room
        self._image.set_pixmap(load_pixmap(room["image"], TIER_COLORS[room["tier"]]))
        style_badge(self._badge, room["tier"])
        self._name.setText(room["name"])
        self._details.setText(room["details"])

        clear_layout(self._chips)
        for i, amenity in enumerate(room["amenities"]):
            self._chips.addWidget(label(amenity, "chipLabel"), i // 3, i % 3, Qt.AlignmentFlag.AlignLeft)
        self._chips.setColumnStretch(3, 1)

        self._day.setText(f"Per Day &nbsp;&nbsp;<b style='color:#c9a84c; font-size:15px;'>{fmt_currency(room['pricePerDay'])}</b>")
        self._hour.setText(f"Per Hour &nbsp;<b style='color:#b8a98e;'>{fmt_currency(room['pricePerHour'])}</b>")
        self._size.setText(f"Size: {room['size']}")
        self._guests.setText(f"Max Guests: {room['maxGuests']} pax")

    def _book(self) -> None:
        if self._room:
            self.go("booking", room=self._room)
