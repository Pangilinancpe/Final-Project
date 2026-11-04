"""
views/payment_view.py — Step 4 of 4: payment method, its details, a separate confirmation pop-up, then save.
compute_totals() lives here because payment is where the final bill is first assembled;
booking_view and receipt_view import it so every screen shows the same numbers.
"""

import re
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QButtonGroup, QDialog, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)

import database
from config import COLORS, FAMILY_DISCOUNT_RATE, PAYMENT_LABELS, PAYMENT_OPTIONS
from utils import badge_pixmap, button, clear_layout, divider, dummy_qr_pixmap, error_box, fmt_currency, label
from views.base_view import BaseView

ACCEPTED, CANCELLED = 1, 2  # results of ConfirmDialog.exec() (0 = the guest went back)


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


def describe_payment(pay: dict) -> str:
    """One-line description of the chosen payment, e.g. 'E-Wallet · GCash · Juan Cruz · 09171234567'."""
    parts = [PAYMENT_LABELS[pay["method"]].split(" (")[0], pay.get("provider"), pay.get("accountName"), pay.get("accountRef")]
    return " · ".join(p for p in parts if p)


class ConfirmDialog(QDialog):
    """Separate pop-up that asks the guest to confirm the transaction. exec() -> ACCEPTED, CANCELLED or 0 (back)."""

    def __init__(self, booking: dict, totals: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Transaction")
        self.setMinimumWidth(480)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(8)
        lay.addWidget(label("CONFIRM TRANSACTION", "sectionKicker"))
        lay.addWidget(label("Please review your payment", "sectionTitle"))
        lay.addWidget(label("Once you confirm, the booking is saved and your receipt is generated.", muted=True, wrap=True))
        lay.addWidget(divider())
        room, plural = booking["room"], "s" if booking["duration"] > 1 else ""
        for caption, value in (("Guests", ", ".join(booking["guestNames"])),
                               ("Room", f"{room['name']} ({room['tier']})"),
                               ("Stay", f"{booking['duration']} {booking['pricingMode']}{plural}"),
                               ("Paid by", f"{booking['payer']['name']} ({booking['payer']['contact']})"),
                               ("Payment", describe_payment(booking["payment"]))):
            row = QHBoxLayout()
            row.addWidget(label(caption, muted=True))
            row.addWidget(label(value, wrap=True, align=Qt.AlignmentFlag.AlignRight), 1)
            lay.addLayout(row)
        lay.addWidget(divider())
        lay.addWidget(label(f"Amount Due: {fmt_currency(totals['grand_total'])}",
                            style=f"font-size:20px; font-weight:800; color:{COLORS['gold']};"))
        lay.addSpacing(6)
        buttons = QHBoxLayout()
        buttons.addWidget(button("← Back", "ghostButton", self.reject))
        buttons.addWidget(button("✕ Cancel booking", "dangerButton", lambda: self.done(CANCELLED)))
        buttons.addWidget(button("Confirm transaction", "primaryButton", self.accept), 1)
        lay.addLayout(buttons)


# logos shown on each checkout row (see utils.badge_pixmap)
ROW_LOGOS = {"gcash": ["gcash"], "maya": ["maya"], "card": ["visa", "mastercard", "discover", "amex"],
             "ebanking": ["bank"], "cash": ["cash"]}
PAGE_W = 1000  # the checkout never gets wider than this, even on a maximised window


class PayRow(QPushButton):
    """One full-width payment choice, like the checkout list: logos on the left, the name on the right."""

    def __init__(self, row_id: str, text: str):
        super().__init__()
        self.row_id = row_id
        self.setObjectName("payRow")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(56)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 18, 0)
        lay.setSpacing(6)
        for kind in ROW_LOGOS[row_id]:
            logo = label()
            logo.setPixmap(badge_pixmap(kind))
            logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lay.addWidget(logo)
        lay.addStretch(1)
        name = label(text, style="font-size:15px;")
        name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(name)


class PaymentView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking, self._option, self._inputs, self._provider = None, None, {}, None
        outer = self.make_page(back=lambda: self.go("services", booking=self._booking), cancel=True)

        # ----- right column: payment methods, details of the chosen one, confirm -----
        right = QVBoxLayout()
        right.setSpacing(10)
        self._group, self._rows = QButtonGroup(self), {}
        for row_id, text, _method, _provider in PAYMENT_OPTIONS:
            row = PayRow(row_id, text)
            row.clicked.connect(lambda _=False, r=row_id: self._select(r))
            self._group.addButton(row)
            self._rows[row_id] = row
            right.addWidget(row)
        self._fields = QVBoxLayout()
        self._error_box, self._error = error_box()
        self._confirm = button("Confirm Booking", "primaryButton", self._confirm_booking)
        self._confirm.setEnabled(False)
        right.addSpacing(4)
        right.addLayout(self._fields)
        right.addWidget(self._error_box)
        right.addWidget(self._confirm)
        right.addWidget(label("By confirming, you agree to the hotel's booking terms and cancellation policy.",
                              style="color:rgb(122, 132, 153); font-size:11px;", wrap=True))
        right.addStretch(1)

        # ----- left column: order summary card -----
        self._card = QFrame()
        self._card.setObjectName("card")
        card_lay = QVBoxLayout(self._card)
        card_lay.setContentsMargins(18, 16, 18, 16)
        card_lay.setSpacing(8)
        self._lines = QVBoxLayout()
        self._lines.setSpacing(8)
        card_lay.addLayout(self._lines)
        left = QVBoxLayout()
        left.addWidget(self._card)
        left.addStretch(1)

        columns = QHBoxLayout()
        columns.setSpacing(28)
        columns.addLayout(left, 5)
        columns.addLayout(right, 5)
        page = QVBoxLayout()
        page.setSpacing(14)
        page.addWidget(label("STEP 4 OF 4", "sectionKicker"))
        page.addWidget(label("🔒  Secure checkout", style="font-size:26px; font-weight:700;"))
        page.addLayout(columns)
        page.addStretch(1)
        holder = QWidget()
        holder.setLayout(page)
        holder.setMaximumWidth(PAGE_W)

        centered = QHBoxLayout()
        centered.addStretch(1)
        centered.addWidget(holder, 10)
        centered.addStretch(1)
        self.add_scroll(outer, centered)

    def on_enter(self, payload: dict) -> None:
        if payload.get("booking") is None:
            return
        self._booking, self._option, self._provider = payload["booking"], None, None
        self._group.setExclusive(False)  # needed to un-check every row
        for row in self._rows.values():
            row.setChecked(False)
        self._group.setExclusive(True)
        self._confirm.setEnabled(False)
        self._confirm.setText("Confirm Booking")
        self._error_box.hide()
        clear_layout(self._fields)
        self._refresh_summary()

    # ----- method-specific fields -----
    def _edit(self, key: str, placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        self._inputs[key] = field
        return field

    def _field_card(self, title: str, *items) -> None:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.addWidget(label(title, style="font-weight:600;"))
        for item in items:
            lay.addLayout(item) if hasattr(item, "addWidget") else lay.addWidget(item)
        self._fields.addWidget(frame)

    def _qr_box(self, provider: str, amount: str) -> QFrame:
        """Sample QR picture (not scannable) for GCash or Maya."""
        box = QFrame()
        box.setObjectName("transparent")
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(label(f"Scan with {provider} to pay {amount}", style="font-weight:600;", align=Qt.AlignmentFlag.AlignCenter))
        picture = label(align=Qt.AlignmentFlag.AlignCenter)
        pm = dummy_qr_pixmap(provider, amount)
        picture.setPixmap(pm)
        picture.setFixedSize(pm.size())  # never let the layout squash the picture
        lay.addWidget(picture)
        lay.addWidget(label("Sample QR (demo only, not a real code)", muted=True, align=Qt.AlignmentFlag.AlignCenter))
        return box

    def _select(self, row_id: str) -> None:
        _id, _text, method, provider = next(o for o in PAYMENT_OPTIONS if o[0] == row_id)
        self._option, self._inputs, self._provider = method, {}, provider
        total = fmt_currency(compute_totals(self._booking)["grand_total"])
        self._confirm.setEnabled(True)
        self._confirm.setText(f"Confirm Booking — {total}")
        self._error_box.hide()
        clear_layout(self._fields)
        if method == "ewallet":
            self._field_card(f"{provider} Payment",
                             label("Scan the QR, then enter the account you paid from.", muted=True),
                             self._qr_box(provider, total), self._edit("name", "Account name"),
                             self._edit("number", "Account number (11 digits)"))
        elif method == "ebanking":
            self._field_card("Online Banking Reference",
                             label("Enter your reference number after completing payment through your banking app.", muted=True, wrap=True),
                             self._edit("ref", "Reference number"))
        elif method == "card":
            mini = QHBoxLayout()
            mini.addWidget(self._edit("expiry", "MM / YY"))
            mini.addWidget(self._edit("cvc", "CVC"))
            self._field_card("Card Details", self._edit("name", "Cardholder name"),
                             self._edit("number", "Card number"), mini)
        else:
            self._field_card("Pay at Front Desk",
                             label("Please proceed to the hotel front desk upon arrival with the exact amount. "
                                   "Your booking will be confirmed upon cash receipt.", muted=True, wrap=True),
                             label(f"Amount Due: {total}", style=f"color:{COLORS['gold']}; font-weight:600;"))

    def _details(self):
        """Check the fields of the chosen method. Returns (payment dict, None) or (None, error message)."""
        v = {k: w.text().strip() for k, w in self._inputs.items()}
        digits = re.sub(r"\D", "", v.get("number", ""))
        pay = dict(method=self._option)
        if self._option == "ewallet":
            if not v["name"]:
                return None, "Enter the e-wallet account name."
            if len(digits) != 11:
                return None, "The e-wallet account number must be 11 digits."
            pay.update(provider=self._provider, accountName=v["name"], accountRef=digits)
        elif self._option == "ebanking":
            if not v["ref"]:
                return None, "Enter your online banking reference number."
            pay.update(accountRef=v["ref"])
        elif self._option == "card":
            if not v["name"]:
                return None, "Enter the cardholder name."
            if not 13 <= len(digits) <= 19:
                return None, "Enter a valid card number (13 to 19 digits)."
            if not re.fullmatch(r"(0[1-9]|1[0-2])\s*/\s*\d{2}", v["expiry"]):
                return None, "The expiry date must look like 08 / 29."
            if not re.fullmatch(r"\d{3,4}", v["cvc"]):
                return None, "The CVC must be 3 or 4 digits."
            pay.update(accountName=v["name"], accountRef="•••• " + digits[-4:])  # never store the full card number
        return pay, None

    def _refresh_summary(self) -> None:
        """Order summary card: room on top (like the item in a store checkout), extras below, total at the bottom."""
        clear_layout(self._lines)
        t, b = compute_totals(self._booking), self._booking
        room, plural = b["room"], "s" if b["duration"] > 1 else ""

        def money_row(left: str, right: str, style: str = "", muted: bool = False) -> QHBoxLayout:
            row = QHBoxLayout()
            row.addWidget(label(left, style=style, muted=muted, wrap=True), 1)
            row.addWidget(label(right, style=style, muted=muted), 0, Qt.AlignmentFlag.AlignRight)
            return row

        self._lines.addLayout(money_row(room["name"], fmt_currency(t["base"]), "font-size:20px; font-weight:700;"))
        self._lines.addWidget(label(f"{room['tier']} room  ·  {b['duration']} {b['pricingMode']}{plural}  ·  "
                                    f"{sum(b['guests'].values())} guest(s)", muted=True))
        if t["has_discount"]:
            self._lines.addWidget(label(f"Family discount  −{fmt_currency(t['discount'])}", style=(
                "color:rgb(74, 222, 128); background-color:rgba(74, 222, 128, 30); border-radius:10px;"
                "padding:3px 10px; font-size:11px; font-weight:600;")), 0, Qt.AlignmentFlag.AlignLeft)
        if t["dining_total"] or t["svc_total"]:
            self._lines.addWidget(divider())
        if t["dining_total"]:
            self._lines.addLayout(money_row("Room service", fmt_currency(t["dining_total"]), muted=True))
        if t["svc_total"]:
            self._lines.addLayout(money_row("Add-on services", fmt_currency(t["svc_total"]), muted=True))
        self._lines.addWidget(divider())
        self._lines.addLayout(money_row("Total", fmt_currency(t["grand_total"]), f"font-size:18px; font-weight:800; color:{COLORS['gold']};"))

    # ----- confirm → pop-up → save → receipt -----
    def _show_error(self, message: str) -> None:
        self._error.setText(message)
        self._error_box.show()

    def _confirm_booking(self) -> None:
        if not self._option:
            return
        pay, error = self._details()
        if error:
            return self._show_error(error)
        self._error_box.hide()
        booking = {**self._booking, "payment": pay}
        totals = compute_totals(booking)
        result = ConfirmDialog(booking, totals, self).exec()
        if result == CANCELLED:
            return self.go("home")
        if result != ACCEPTED:
            return
        booking.update(reference=database.make_reference(), createdAt=datetime.now())
        try:
            database.save_booking(booking, totals)
        except Exception as exc:
            return QMessageBox.critical(self, "Could not save", f"The booking could not be saved:\n{exc}")
        self.go("receipt", booking=booking)
