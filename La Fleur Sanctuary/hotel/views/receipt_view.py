"""views/receipt_view.py — confirmation screen with the itemised receipt."""

import random
import string
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QVBoxLayout

from config import COLORS, HOTEL_HOTLINE, HOTEL_LOCATION, HOTEL_NAME, PAYMENT_LABELS
from utils import button, clear_layout, divider, fmt_currency, label
from views.base_view import BaseView
from views.payment_view import compute_totals

GOLD, GREEN, CENTER = COLORS["gold"], COLORS["green"], Qt.AlignmentFlag.AlignCenter
GOLD_BOLD = f"color:{GOLD}; font-weight:600;"


def make_reference() -> str:
    """Random reference number like HB-7K2P9XQ4."""
    return "HB-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def line_row(left: str, right: str = "", style: str = "") -> QHBoxLayout:
    """One receipt line: description on the left, amount on the right."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 2, 0, 2)
    row.addWidget(label(left, style=style, wrap=True), 1)
    row.addWidget(label(right, style=style, align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
    return row


class ReceiptView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        outer = self.make_page()

        self._card = QFrame()
        self._card.setObjectName("card")
        self._card.setMaximumWidth(560)
        self._content = QVBoxLayout(self._card)
        self._content.setContentsMargins(28, 24, 28, 24)
        self._content.setSpacing(4)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(button("Print", "ghostButton", self._print))
        buttons.addWidget(button("Done", "primaryButton", lambda: self.go("home")))
        buttons.addStretch(1)

        body = QVBoxLayout()
        body.addWidget(self._card, alignment=Qt.AlignmentFlag.AlignHCenter)
        body.addLayout(buttons)
        body.addStretch(1)
        self.add_scroll(outer, body)

    def on_enter(self, payload: dict) -> None:
        if payload.get("booking") is None:
            return
        self._booking = payload["booking"]
        self._build_receipt()

    def _build_receipt(self) -> None:
        clear_layout(self._content)
        b, c = self._booking, self._content
        t, room, guests, info = compute_totals(b), b["room"], b["guests"], b["customer"]
        mode, plural = b["pricingMode"], "s" if b["duration"] > 1 else ""
        breakdown = ", ".join(f"{k.capitalize()}: {n}" for k, n in guests.items() if n)
        row = lambda *args: c.addLayout(line_row(*args))

        c.addWidget(label(HOTEL_NAME, style=f"font-size:22px; font-weight:800; color:{GOLD};", align=CENTER))
        c.addWidget(label(HOTEL_LOCATION, muted=True, align=CENTER))
        c.addWidget(label(f"Hotline: {HOTEL_HOTLINE}", muted=True, align=CENTER))
        c.addSpacing(8)
        c.addWidget(divider())
        c.addWidget(label("BOOKING RECEIPT", style="font-weight:600; font-size:15px;", align=CENTER))
        row("Reference No.", make_reference(), GOLD_BOLD)
        row("Date", datetime.now().strftime("%B %d, %Y  %I:%M %p"))
        c.addWidget(divider())

        row("GUEST DETAILS", "", GOLD_BOLD)
        row("Name", info["name"])
        row("Contact", info["contact"])
        row("Email", info["email"])
        row("Guests", f"{sum(guests.values())} ({breakdown})")
        row("Room", f"{room['name']} ({room['tier']})")
        row("Payment Method", PAYMENT_LABELS.get(b.get("payment"), "-"))
        c.addWidget(divider())

        row("CHARGES", "", GOLD_BOLD)
        row(f"Room ({b['duration']} {mode}{plural})", fmt_currency(t["base"]))
        if t["has_discount"]:
            row("Family Discount (10%)", f"−{fmt_currency(t['discount'])}", f"color:{GREEN};")
        for entry in (*b["dining"], *b["extraServices"]):
            row(f"{entry['item']['name']} × {entry['qty']}", fmt_currency(entry["item"]["price"] * entry["qty"]))

        c.addWidget(divider())
        row("TOTAL AMOUNT DUE", fmt_currency(t["grand_total"]), f"font-weight:800; font-size:17px; color:{GOLD};")
        c.addSpacing(10)
        c.addWidget(label("Thank you for staying with us!", muted=True, align=CENTER))

    def _print(self) -> None:
        QMessageBox.information(self, "Print", "Printing is not available yet.")
