"""
views/services_view.py
Step 3 of 4: optional add-on services, shown as a grid of qty-adjustable
cards. Equivalent of the React <ServicesView/>.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from data import SERVICES, find_service_item
from utils import fmt_currency
from views.base_view import BaseView


class ServicesView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        self._selected: dict = {}
        self._qty_labels: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghostButton")
        back_btn.clicked.connect(self._back)
        outer.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        kicker = QLabel("STEP 3 OF 4")
        kicker.setObjectName("sectionKicker")
        outer.addWidget(kicker)
        title = QLabel("Additional Services")
        title.setObjectName("sectionTitle")
        outer.addWidget(title)
        sub = QLabel("Enhance your stay with our curated add-ons.")
        sub.setProperty("class", "muted")
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        grid_host = QWidget()
        self._grid = QGridLayout(grid_host)
        self._grid.setSpacing(16)
        scroll.setWidget(grid_host)

        for i, svc in enumerate(SERVICES):
            self._grid.addWidget(self._service_card(svc), i // 2, i % 2)

        btn_row = QHBoxLayout()
        skip_btn = QPushButton("Skip")
        skip_btn.setObjectName("ghostButton")
        skip_btn.clicked.connect(self._skip)
        continue_btn = QPushButton("Continue to Payment →")
        continue_btn.setObjectName("primaryButton")
        continue_btn.clicked.connect(self._continue)
        btn_row.addWidget(skip_btn)
        btn_row.addWidget(continue_btn, 1)
        outer.addLayout(btn_row)

    def on_enter(self, payload: dict) -> None:
        booking = payload.get("booking")
        if booking is None:
            return
        self._booking = booking
        self._selected = {}
        for label in self._qty_labels.values():
            label.setText("0")

    def _service_card(self, svc: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        name = QLabel(f"<b>{svc['name']}</b>")
        name.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(name)

        desc = QLabel(svc["description"])
        desc.setProperty("class", "muted")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        bottom_row = QHBoxLayout()
        price = QLabel(fmt_currency(svc["price"]))
        price.setStyleSheet("color:#c9a84c; font-weight:600;")
        bottom_row.addWidget(price)
        bottom_row.addStretch(1)

        minus = QPushButton("−")
        minus.setObjectName("qtyButton")
        minus.clicked.connect(lambda _checked, i=svc["id"]: self._adjust(i, -1))
        bottom_row.addWidget(minus)

        qty_label = QLabel("0")
        qty_label.setFixedWidth(24)
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_labels[svc["id"]] = qty_label
        bottom_row.addWidget(qty_label)

        plus = QPushButton("+")
        plus.setObjectName("qtyButton")
        plus.clicked.connect(lambda _checked, i=svc["id"]: self._adjust(i, 1))
        bottom_row.addWidget(plus)

        layout.addLayout(bottom_row)
        return card

    def _adjust(self, item_id: int, delta: int) -> None:
        new_qty = max(0, self._selected.get(item_id, 0) + delta)
        if new_qty == 0:
            self._selected.pop(item_id, None)
        else:
            self._selected[item_id] = new_qty
        self._qty_labels[item_id].setText(str(new_qty))

    def _services_list(self) -> list:
        return [dict(item=find_service_item(iid), qty=qty) for iid, qty in self._selected.items()]

    def _continue(self) -> None:
        booking = {**self._booking, "extraServices": self._services_list()}
        self.go("payment", booking=booking)

    def _skip(self) -> None:
        booking = {**self._booking, "extraServices": []}
        self.go("payment", booking=booking)

    def _back(self) -> None:
        self.go("dining", booking=self._booking)
