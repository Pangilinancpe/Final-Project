"""
views/payment_view.py
Step 4 of 4: payment method selection, method-specific fields, and the bill
summary sidebar. Equivalent of the React <PaymentView/>.

compute_totals() also lives here (rather than a separate module) since
payment is where the final bill is first assembled — receipt_view.py
imports it from here to redisplay the same numbers on the confirmation
screen.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from config import FAMILY_DISCOUNT_RATE, PAYMENT_METHODS
from utils import fmt_currency
from views.base_view import BaseView


def compute_totals(booking: dict) -> dict:
    unit_price = booking["room"]["pricePerDay"] if booking["pricingMode"] == "day" else booking["room"]["pricePerHour"]
    base = unit_price * booking["duration"]

    has_discount = booking["guests"]["seniors"] > 0 or booking["guests"]["children"] > 0
    discount = round(base * FAMILY_DISCOUNT_RATE) if has_discount else 0
    room_total = base - discount

    dining_total = sum(d["item"]["price"] * d["qty"] for d in booking["dining"])
    svc_total = sum(s["item"]["price"] * s["qty"] for s in booking["extraServices"])
    grand_total = room_total + dining_total + svc_total

    return dict(
        base=base, has_discount=has_discount, discount=discount, room_total=room_total,
        dining_total=dining_total, svc_total=svc_total, grand_total=grand_total,
    )


class PaymentView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        self._method = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghostButton")
        back_btn.clicked.connect(self._back)
        outer.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        row = QHBoxLayout(body)
        row.setSpacing(24)

        left = QVBoxLayout()
        kicker = QLabel("STEP 4 OF 4")
        kicker.setObjectName("sectionKicker")
        left.addWidget(kicker)
        title = QLabel("Payment")
        title.setObjectName("sectionTitle")
        left.addWidget(title)

        method_grid = QGridLayout()
        self._method_group = QButtonGroup(self)
        self._method_group.setExclusive(True)
        for i, (key, label, icon) in enumerate(PAYMENT_METHODS):
            btn = QPushButton(f"{icon}  {label}")
            btn.setObjectName("paymentOption")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, k=key: self._select_method(k))
            self._method_group.addButton(btn)
            method_grid.addWidget(btn, i // 2, i % 2)
        left.addLayout(method_grid)

        self._fields_host = QVBoxLayout()
        left.addLayout(self._fields_host)

        self._confirm_btn = QPushButton("Confirm Booking")
        self._confirm_btn.setObjectName("primaryButton")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.clicked.connect(self._confirm)
        left.addWidget(self._confirm_btn)

        row.addLayout(left, 2)
        row.addWidget(self._build_sidebar(), 0, Qt.AlignmentFlag.AlignTop)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout(sidebar)
        layout.addWidget(self._bold("Bill Summary"))

        self._summary_lines = QVBoxLayout()
        layout.addLayout(self._summary_lines)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self._grand_total_label = QLabel()
        self._grand_total_label.setStyleSheet("font-weight:800; font-size:15px; color:#c9a84c;")
        layout.addWidget(self._grand_total_label)
        layout.addStretch(1)
        self._sidebar_ref = sidebar
        return sidebar

    @staticmethod
    def _bold(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight:600;")
        return label

    def on_enter(self, payload: dict) -> None:
        booking = payload.get("booking")
        if booking is None:
            return
        self._booking = booking
        self._method = None

        self._method_group.setExclusive(False)
        for btn in self._method_group.buttons():
            btn.setChecked(False)
        self._method_group.setExclusive(True)

        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setText("Confirm Booking")
        self._clear_fields()
        self._refresh_summary()

    def _clear_fields(self) -> None:
        while self._fields_host.count():
            item = self._fields_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _select_method(self, key: str) -> None:
        self._method = key
        totals = compute_totals(self._booking)
        self._confirm_btn.setEnabled(True)
        self._confirm_btn.setText(f"Confirm Booking — {fmt_currency(totals['grand_total'])}")
        self._clear_fields()

        if key == "card":
            frame = QFrame()
            frame.setObjectName("card")
            layout = QVBoxLayout(frame)
            layout.addWidget(self._bold("Card Details (Demo)"))
            name_input = QLineEdit()
            name_input.setPlaceholderText("Cardholder Name")
            number_input = QLineEdit()
            number_input.setPlaceholderText("4242 4242 4242 4242")
            mini_row = QHBoxLayout()
            expiry_input = QLineEdit()
            expiry_input.setPlaceholderText("MM / YY")
            cvc_input = QLineEdit()
            cvc_input.setPlaceholderText("CVC")
            mini_row.addWidget(expiry_input)
            mini_row.addWidget(cvc_input)
            layout.addWidget(name_input)
            layout.addWidget(number_input)
            layout.addLayout(mini_row)
            self._fields_host.addWidget(frame)

        elif key in ("ewallet", "ebanking"):
            label_text = "E-Wallet" if key == "ewallet" else "Online Banking"
            frame = QFrame()
            frame.setObjectName("card")
            layout = QVBoxLayout(frame)
            layout.addWidget(self._bold(f"{label_text} Reference"))
            note = QLabel("Enter your reference number after completing payment through your app.")
            note.setProperty("class", "muted")
            note.setWordWrap(True)
            layout.addWidget(note)
            ref_input = QLineEdit()
            ref_input.setPlaceholderText("e.g. GC-2026-XXXXXXXXXXXX")
            layout.addWidget(ref_input)
            self._fields_host.addWidget(frame)

        elif key == "cash":
            frame = QFrame()
            frame.setObjectName("card")
            layout = QVBoxLayout(frame)
            layout.addWidget(self._bold("Pay at Front Desk"))
            note = QLabel(
                "Please proceed to the hotel front desk upon arrival with the exact amount. "
                "Your booking will be confirmed upon cash receipt."
            )
            note.setProperty("class", "muted")
            note.setWordWrap(True)
            layout.addWidget(note)
            amount = QLabel(f"Amount Due: {fmt_currency(totals['grand_total'])}")
            amount.setStyleSheet("color:#c9a84c; font-weight:600;")
            layout.addWidget(amount)
            self._fields_host.addWidget(frame)

    def _refresh_summary(self) -> None:
        while self._summary_lines.count():
            item = self._summary_lines.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        totals = compute_totals(self._booking)
        duration = self._booking["duration"]
        mode = self._booking["pricingMode"]
        plural = "s" if duration > 1 else ""

        def add_line(text: str, style: str = "") -> None:
            label = QLabel(text)
            if style:
                label.setStyleSheet(style)
            else:
                label.setProperty("class", "muted")
            self._summary_lines.addWidget(label)

        add_line(f"Room ({duration} {mode}{plural}): {fmt_currency(totals['base'])}")
        if totals["has_discount"]:
            add_line(f"Family Discount: −{fmt_currency(totals['discount'])}", "color:#4ade80;")
        if totals["dining_total"] > 0:
            add_line(f"Room Service: {fmt_currency(totals['dining_total'])}")
        if totals["svc_total"] > 0:
            add_line(f"Add-on Services: {fmt_currency(totals['svc_total'])}")

        self._grand_total_label.setText(f"Grand Total: {fmt_currency(totals['grand_total'])}")

    def _confirm(self) -> None:
        if not self._method:
            return
        booking = {**self._booking, "payment": self._method}
        self.go("receipt", booking=booking)

    def _back(self) -> None:
        self.go("services", booking=self._booking)
