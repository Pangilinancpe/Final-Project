"""views/dining_view.py — Step 2 of 4: optional room-service pre-order."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QVBoxLayout

from config import COLORS
from data import DINING, find_dining_item
from utils import Stepper, button, clear_layout, divider, fmt_currency, label, sidebar_card
from views.base_view import BaseView

GOLD = COLORS["gold"]


class DiningView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking, self._orders, self._category = None, {}, "All"
        outer = self.make_page(back=self._back, cancel=True)

        left = QVBoxLayout()
        left.addWidget(label("STEP 2 OF 4", "sectionKicker"))
        left.addWidget(label("Room Service Menu", "sectionTitle"))
        left.addWidget(label("Pre-order dining for your stay. Items will be delivered to your room.", muted=True))
        combo = QComboBox()
        combo.addItems(["All"] + sorted({d["category"] for d in DINING}))
        combo.currentTextChanged.connect(self._set_category)
        left.addWidget(combo)
        self._items = QVBoxLayout()
        left.addLayout(self._items)
        left.addStretch(1)

        card, lay = sidebar_card("Dining Order")
        self._lines = QVBoxLayout()
        self._empty = label("No items selected yet.", muted=True)
        self._total = label(style=f"font-weight:700; color:{GOLD};")
        for w in (self._lines, self._empty, divider(), self._total,
                  button("Continue to Services →", "primaryButton", self._continue),
                  button("Skip dining →", "ghostButton", self._skip)):
            lay.addLayout(w) if isinstance(w, QVBoxLayout) else lay.addWidget(w)
        lay.addStretch(1)

        row = QHBoxLayout()
        row.setSpacing(24)
        row.addLayout(left, 2)
        row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self.add_scroll(outer, row)
        self._rebuild_items()
        self._refresh_sidebar()

    def on_enter(self, payload: dict) -> None:
        if payload.get("booking") is None:
            return
        self._booking = payload["booking"]
        self._orders = {d["item"]["id"]: d["qty"] for d in self._booking.get("dining", [])}  # restores on Back
        self._rebuild_items()
        self._refresh_sidebar()

    def _set_category(self, text: str) -> None:
        self._category = text
        self._rebuild_items()

    def _rebuild_items(self) -> None:
        clear_layout(self._items)
        for item in DINING:
            if self._category in ("All", item["category"]):
                self._items.addWidget(self._item_row(item))

    def _item_row(self, item: dict) -> QFrame:
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 6, 0, 6)
        text, name_row = QVBoxLayout(), QHBoxLayout()
        name_row.addWidget(label(f"<b>{item['name']}</b>"))
        name_row.addWidget(label(item["category"], muted=True))
        name_row.addStretch(1)
        text.addLayout(name_row)
        text.addWidget(label(item["description"], muted=True, wrap=True))
        lay.addLayout(text, 1)
        lay.addWidget(label(fmt_currency(item["price"]), style=f"color:{GOLD}; font-weight:600;"))
        stepper = Stepper(self._orders.get(item["id"], 0))
        stepper.changed.connect(lambda qty, i=item["id"]: self._set_qty(i, qty))
        lay.addWidget(stepper)
        return frame

    def _set_qty(self, item_id: int, qty: int) -> None:
        if qty:
            self._orders[item_id] = qty
        else:
            self._orders.pop(item_id, None)
        self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        clear_layout(self._lines)
        self._empty.setVisible(not self._orders)
        total = 0
        for item_id, qty in self._orders.items():
            item = find_dining_item(item_id)
            total += item["price"] * qty
            self._lines.addWidget(label(f"{item['name']} ×{qty} — {fmt_currency(item['price'] * qty)}", muted=True))
        self._total.setText(f"Dining Total: {fmt_currency(total)}")

    def _next(self, with_orders: bool) -> None:
        dining = [dict(item=find_dining_item(i), qty=q) for i, q in self._orders.items()] if with_orders else []
        self.go("services", booking={**self._booking, "dining": dining})

    def _continue(self) -> None:
        self._next(True)

    def _skip(self) -> None:
        self._next(False)

    def _back(self) -> None:
        self.go("booking", room=self._booking["room"], booking=self._booking)
