
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QScrollArea, QVBoxLayout, QWidget,
)

from config import TIER_COLORS
from data import ROOMS
from utils import fmt_currency, load_pixmap
from views.base_view import BaseView


class RoomsView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tier_filter = "All"
        self._pricing_mode = "day"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(18)

        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        kicker = QLabel("AVAILABLE ROOMS")
        kicker.setObjectName("sectionKicker")
        title = QLabel("Choose Your Room")
        title.setObjectName("sectionTitle")
        title_col.addWidget(kicker)
        title_col.addWidget(title)
        header_row.addLayout(title_col)
        header_row.addStretch(1)

        self._day_radio = QRadioButton("Per Day")
        self._hour_radio = QRadioButton("Per Hour")
        self._day_radio.setChecked(True)
        rate_group = QButtonGroup(self)
        rate_group.addButton(self._day_radio)
        rate_group.addButton(self._hour_radio)
        self._day_radio.toggled.connect(self._on_rate_changed)
        header_row.addWidget(self._day_radio)
        header_row.addWidget(self._hour_radio)

        self._tier_combo = QComboBox()
        self._tier_combo.addItems(["All", "Premium", "Deluxe", "Economy"])
        self._tier_combo.currentTextChanged.connect(self._on_tier_changed)
        header_row.addWidget(self._tier_combo)

        outer.addLayout(header_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        self._grid_host = QWidget()
        self._grid = QGridLayout(self._grid_host)
        self._grid.setSpacing(18)
        scroll.setWidget(self._grid_host)

        self._refresh_grid()

    def on_enter(self, payload: dict) -> None:
        tier = payload.get("tier_filter")
        if tier:
            self._tier_filter = tier
            self._tier_combo.blockSignals(True)
            self._tier_combo.setCurrentText(tier)
            self._tier_combo.blockSignals(False)
            self._refresh_grid()

    def _on_rate_changed(self, _checked: bool) -> None:
        self._pricing_mode = "day" if self._day_radio.isChecked() else "hour"
        self._refresh_grid()

    def _on_tier_changed(self, text: str) -> None:
        self._tier_filter = text
        self._refresh_grid()

    def _refresh_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        rooms = ROOMS if self._tier_filter == "All" else [r for r in ROOMS if r["tier"] == self._tier_filter]
        for i, room in enumerate(rooms):
            self._grid.addWidget(self._room_card(room), i // 3, i % 3)

    def _room_card(self, room: dict) -> QFrame:
        color = TIER_COLORS[room["tier"]]
        price = room["pricePerDay"] if self._pricing_mode == "day" else room["pricePerHour"]

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 14)
        layout.setSpacing(6)

        image_label = QLabel()
        image_label.setFixedHeight(150)
        image_label.setScaledContents(True)
        image_label.setPixmap(load_pixmap(room["image"]))
        layout.addWidget(image_label)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(14, 8, 14, 0)
        text_col.setSpacing(4)

        badge = QLabel(room["tier"])
        badge.setStyleSheet(
            f"color:{color}; background-color:{color}1a; border:1px solid {color}55;"
            "border-radius:4px; padding:2px 8px; font-size:10px;"
        )
        badge.setFixedWidth(badge.sizeHint().width() + 4)
        text_col.addWidget(badge)

        name = QLabel(room["name"])
        name.setStyleSheet("font-weight:600; font-size:13px;")
        text_col.addWidget(name)

        price_label = QLabel(
            f"<span style='color:#c9a84c; font-weight:700; font-size:17px;'>{fmt_currency(price)}</span>"
            f"<span style='color:#7a8499;'> /{self._pricing_mode}</span>"
        )
        price_label.setTextFormat(Qt.TextFormat.RichText)
        text_col.addWidget(price_label)

        meta = QLabel(f"{room['size']} · Up to {room['maxGuests']} guests")
        meta.setProperty("class", "muted")
        text_col.addWidget(meta)

        layout.addLayout(text_col)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(14, 6, 14, 0)
        details_btn = QPushButton("Details")
        details_btn.setObjectName("ghostButton")
        details_btn.clicked.connect(lambda _checked, r=room: self.go("room_detail", room=r))
        book_btn = QPushButton("Book")
        book_btn.setObjectName("primaryButton")
        book_btn.clicked.connect(lambda _checked, r=room: self.go("booking", room=r))
        btn_row.addWidget(details_btn)
        btn_row.addWidget(book_btn)
        layout.addLayout(btn_row)

        return card
