"""
views/payment_view.py — Step 4 of 4: payment method, method-specific fields, bill summary.
compute_totals() lives here because payment is where the final bill is first assembled;
booking_view and receipt_view import it so every screen shows the same numbers.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from config import COLORS, FAMILY_DISCOUNT_RATE, PAYMENT_METHODS
from utils import button, clear_layout, divider, fmt_currency, label, sidebar_card
from views.base_view import BaseView


def compute_totals(booking: dict) -> dict:
    room = booking["room"]
    unit_price = room["pricePerDay"] if booking["pricingMode"] == "day" else room["pricePerHour"]
    base = unit_price * booking["duration"]
    has_discount = booking["guests"]["seniors"] > 0 or booking["guests"]["children"] > 0
    discount = round(base * FAMILY_DISCOUNT_RATE) if has_discount else 0
    dining_total = sum(d["item"]["price"] * d["qty"] for d in booking["dining"])
    svc_total = sum(s["item"]["price"] * s["qty"] for s in booking["extraServices"])
    return dict(base=base, has_discount=has_discount, discount=discount, room_total=base - discount,
                dining_total=dining_total, svc_total=svc_total, grand_total=base - discount + dining_total + svc_total)


def _edit(placeholder: str) -> QLineEdit:
    field = QLineEdit()
    field.setPlaceholderText(placeholder)
    return field


class PaymentView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        outer = self.make_page(back=lambda: self.go("services", booking=self._booking), cancel=True)

        left = QVBoxLayout()
        left.addWidget(label("STEP 4 OF 4", "sectionKicker"))
        left.addWidget(label("Payment", "sectionTitle"))
        grid, self._group = QGridLayout(), QButtonGroup(self)
        for i, (key, text, icon) in enumerate(PAYMENT_METHODS):
            btn = button(f"{icon}  {text}", "paymentOption", lambda _=False, k=key: self._select(k))
            btn.setCheckable(True)
            self._group.addButton(btn)
            grid.addWidget(btn, i // 2, i % 2)
        self._fields = QVBoxLayout()
        self._confirm = button("Confirm Booking", "primaryButton", self._confirm_booking)
        self._confirm.setEnabled(False)
        self._method = None
        left.addLayout(grid)
        left.addLayout(self._fields)
        left.addWidget(self._confirm)
        left.addStretch(1)

        card, lay = sidebar_card("Bill Summary")
        self._lines = QVBoxLayout()
        self._grand = label(style=f"font-weight:800; font-size:15px; color:{COLORS['gold']};")
        lay.addLayout(self._lines)
        lay.addWidget(divider())
        lay.addWidget(self._grand)
        lay.addStretch(1)

        row = QHBoxLayout()
        row.setSpacing(24)
        row.addLayout(left, 2)
        row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self.add_scroll(outer, row)

    def on_enter(self, payload: dict) -> None:
        if payload.get("booking") is None:
            return
        self._booking, self._method = payload["booking"], None
        self._group.setExclusive(False)  # needed to un-check every button
        for btn in self._group.buttons():
            btn.setChecked(False)
        self._group.setExclusive(True)
        self._confirm.setEnabled(False)
        self._confirm.setText("Confirm Booking")
        clear_layout(self._fields)
        self._refresh_summary()

    def _field_card(self, title: str, *items) -> None:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.addWidget(label(title, style="font-weight:600;"))
        for item in items:
            lay.addWidget(item) if isinstance(item, QWidget) else lay.addLayout(item)
        self._fields.addWidget(frame)

    def _select(self, key: str) -> None:
        self._method = key
        total = fmt_currency(compute_totals(self._booking)["grand_total"])
        self._confirm.setEnabled(True)
        self._confirm.setText(f"Confirm Booking — {total}")
        clear_layout(self._fields)
        if key == "card":
            mini = QHBoxLayout()
            mini.addWidget(_edit("MM / YY"))
            mini.addWidget(_edit("CVC"))
            self._field_card("Card Details (Demo)", _edit("Cardholder Name"), _edit("4242 4242 4242 4242"), mini)
        elif key in ("ewallet", "ebanking"):
            self._field_card(("E-Wallet" if key == "ewallet" else "Online Banking") + " Reference",
                             label("Enter your reference number after completing payment through your app.", muted=True, wrap=True),
                             _edit("e.g. GC-2026-XXXXXXXXXXXX"))
        else:
            self._field_card("Pay at Front Desk",
                             label("Please proceed to the hotel front desk upon arrival with the exact amount. "
                                   "Your booking will be confirmed upon cash receipt.", muted=True, wrap=True),
                             label(f"Amount Due: {total}", style=f"color:{COLORS['gold']}; font-weight:600;"))

    def _refresh_summary(self) -> None:
        clear_layout(self._lines)
        t, b = compute_totals(self._booking), self._booking
        rows = [(f"Room ({b['duration']} {b['pricingMode']}{'s' if b['duration'] > 1 else ''}): {fmt_currency(t['base'])}", False)]
        if t["has_discount"]:
            rows.append((f"Family Discount: −{fmt_currency(t['discount'])}", True))
        if t["dining_total"]:
            rows.append((f"Room Service: {fmt_currency(t['dining_total'])}", False))
        if t["svc_total"]:
            rows.append((f"Add-on Services: {fmt_currency(t['svc_total'])}", False))
        for text, green in rows:
            self._lines.addWidget(label(text, muted=not green, style=f"color:{COLORS['green']};" if green else ""))
        self._grand.setText(f"Grand Total: {fmt_currency(t['grand_total'])}")

    def _confirm_booking(self) -> None:
        if self._method:
            self.go("receipt", booking={**self._booking, "payment": self._method})
