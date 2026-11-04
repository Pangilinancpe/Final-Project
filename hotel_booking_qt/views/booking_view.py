"""
views/booking_view.py
Step 1 of 4: pricing & duration, guest composition, and customer details
form, with validation and a live-updating price summary. Equivalent of the
React <BookingView/>.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from config import FAMILY_DISCOUNT_RATE, MAX_GUESTS_SPIN, MIN_GUESTS, TIER_COLORS
from utils import fmt_currency, load_pixmap
from views.base_view import BaseView


class BookingView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._room = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(14)

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
        left.setSpacing(14)

        kicker = QLabel("STEP 1 OF 4")
        kicker.setObjectName("sectionKicker")
        left.addWidget(kicker)
        title = QLabel("Booking Details")
        title.setObjectName("sectionTitle")
        left.addWidget(title)

        self._error_box = QFrame()
        self._error_box.setObjectName("errorBox")
        self._error_layout = QVBoxLayout(self._error_box)
        self._error_box.hide()
        left.addWidget(self._error_box)

        left.addWidget(self._build_pricing_card())
        left.addWidget(self._build_guests_card())
        left.addWidget(self._build_customer_card())

        continue_btn = QPushButton("Continue to Dining & Services →")
        continue_btn.setObjectName("primaryButton")
        continue_btn.clicked.connect(self._continue)
        left.addWidget(continue_btn)

        row.addLayout(left, 2)
        row.addWidget(self._build_sidebar(), 0, Qt.AlignmentFlag.AlignTop)

        for spin in (self._adults_spin, self._seniors_spin, self._children_spin):
            spin.valueChanged.connect(self._update_summary)

    # ---- card builders -----------------------------------------------

    def _build_pricing_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.addWidget(self._bold("Pricing & Duration"))

        rate_row = QHBoxLayout()
        self._day_radio = QRadioButton("Per Day")
        self._hour_radio = QRadioButton("Per Hour")
        self._day_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self._day_radio)
        group.addButton(self._hour_radio)
        self._day_radio.toggled.connect(self._on_rate_changed)
        rate_row.addWidget(self._day_radio)
        rate_row.addWidget(self._hour_radio)
        rate_row.addStretch(1)
        layout.addLayout(rate_row)

        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel("Duration:"))
        self._duration_spin = QSpinBox()
        self._duration_spin.setMinimum(1)
        self._duration_spin.setMaximum(30)
        self._duration_spin.setValue(1)
        self._duration_spin.valueChanged.connect(self._update_summary)
        duration_row.addWidget(self._duration_spin)
        duration_row.addStretch(1)
        layout.addLayout(duration_row)

        self._price_breakdown_label = QLabel()
        self._price_breakdown_label.setProperty("class", "muted")
        layout.addWidget(self._price_breakdown_label)
        return card

    def _build_guests_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.addWidget(self._bold("Guest Composition"))

        hint = QLabel(
            f"Minimum {MIN_GUESTS} guests required · Senior & child guests qualify for "
            f"{int(FAMILY_DISCOUNT_RATE * 100)}% discount"
        )
        hint.setProperty("class", "muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._guest_count_label = QLabel()
        layout.addWidget(self._guest_count_label)

        guests_row = QHBoxLayout()
        self._adults_spin = self._labeled_spin(guests_row, "Adults", 0, MAX_GUESTS_SPIN, 2)
        self._seniors_spin = self._labeled_spin(guests_row, "Seniors (60+) ✦", 0, MAX_GUESTS_SPIN, 0)
        self._children_spin = self._labeled_spin(guests_row, "Children (<12) ✦", 0, MAX_GUESTS_SPIN, 0)
        layout.addLayout(guests_row)
        return card

    def _build_customer_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.addWidget(self._bold("Customer Details"))

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Full Name *  (e.g. Juan dela Cruz)")
        layout.addWidget(self._name_input)

        contact_row = QHBoxLayout()
        self._contact_input = QLineEdit()
        self._contact_input.setPlaceholderText("Contact Number *")
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Email Address *")
        contact_row.addWidget(self._contact_input)
        contact_row.addWidget(self._email_input)
        layout.addLayout(contact_row)

        mop_row = QHBoxLayout()
        self._mop_input = QLineEdit()
        self._mop_input.setPlaceholderText("Mode of Payment (e.g. GCash, BDO Card)")
        self._account_input = QLineEdit()
        self._account_input.setPlaceholderText("Account / Card Number")
        mop_row.addWidget(self._mop_input)
        mop_row.addWidget(self._account_input)
        layout.addLayout(mop_row)
        return card

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout(sidebar)

        self._sidebar_image = QLabel()
        self._sidebar_image.setFixedHeight(120)
        self._sidebar_image.setScaledContents(True)
        layout.addWidget(self._sidebar_image)

        self._sidebar_badge = QLabel()
        layout.addWidget(self._sidebar_badge)

        self._sidebar_name = QLabel()
        self._sidebar_name.setStyleSheet("font-weight:600;")
        layout.addWidget(self._sidebar_name)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self._sidebar_base = QLabel()
        layout.addWidget(self._sidebar_base)
        self._sidebar_discount = QLabel()
        layout.addWidget(self._sidebar_discount)
        self._sidebar_subtotal = QLabel()
        layout.addWidget(self._sidebar_subtotal)
        layout.addStretch(1)
        return sidebar

    # ---- small helpers --------------------------------------------------

    @staticmethod
    def _bold(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight:600;")
        return label

    @staticmethod
    def _labeled_spin(row: QHBoxLayout, label_text: str, lo: int, hi: int, default: int) -> QSpinBox:
        col = QVBoxLayout()
        label = QLabel(label_text)
        label.setProperty("class", "muted")
        spin = QSpinBox()
        spin.setRange(lo, hi)
        spin.setValue(default)
        col.addWidget(label)
        col.addWidget(spin)
        row.addLayout(col)
        return spin

    # ---- lifecycle / behavior -------------------------------------------

    def on_enter(self, payload: dict) -> None:
        room = payload.get("room")
        if room is None:
            return
        self._room = room

        self._day_radio.setChecked(True)
        self._duration_spin.setMaximum(30)
        self._duration_spin.setValue(1)
        self._adults_spin.setValue(2)
        self._seniors_spin.setValue(0)
        self._children_spin.setValue(0)
        self._name_input.clear()
        self._contact_input.clear()
        self._email_input.clear()
        self._mop_input.clear()
        self._account_input.clear()
        self._error_box.hide()

        self._sidebar_image.setPixmap(load_pixmap(room["image"]))
        color = TIER_COLORS[room["tier"]]
        self._sidebar_badge.setText(room["tier"])
        self._sidebar_badge.setStyleSheet(
            f"color:{color}; background-color:{color}1a; border:1px solid {color}55;"
            "border-radius:4px; padding:2px 8px; font-size:10px;"
        )
        self._sidebar_badge.setFixedWidth(self._sidebar_badge.sizeHint().width() + 4)
        self._sidebar_name.setText(room["name"])

        self._update_summary()

    def _on_rate_changed(self, _checked: bool) -> None:
        self._duration_spin.setMaximum(24 if self._hour_radio.isChecked() else 30)
        self._duration_spin.setValue(1)
        self._update_summary()

    def _mode(self) -> str:
        return "day" if self._day_radio.isChecked() else "hour"

    def _unit_price(self) -> float:
        return self._room["pricePerDay"] if self._mode() == "day" else self._room["pricePerHour"]

    def _update_summary(self) -> None:
        if self._room is None:
            return
        duration = self._duration_spin.value()
        unit_price = self._unit_price()
        base = unit_price * duration
        has_discount = self._seniors_spin.value() > 0 or self._children_spin.value() > 0
        discount = round(base * FAMILY_DISCOUNT_RATE) if has_discount else 0
        subtotal = base - discount
        plural = "s" if duration > 1 else ""

        self._price_breakdown_label.setText(
            f"{fmt_currency(unit_price)} × {duration} {self._mode()}{plural} = {fmt_currency(base)}"
        )

        total_guests = self._adults_spin.value() + self._seniors_spin.value() + self._children_spin.value()
        color = "#4ade80" if total_guests >= MIN_GUESTS else "#f87171"
        self._guest_count_label.setText(f"{total_guests} total guest{'s' if total_guests != 1 else ''}")
        self._guest_count_label.setStyleSheet(f"color:{color};")

        self._sidebar_base.setText(f"Base ({duration} {self._mode()}{plural}): {fmt_currency(base)}")
        if has_discount:
            self._sidebar_discount.setText(f"Family Discount (10%): −{fmt_currency(discount)}")
            self._sidebar_discount.setStyleSheet("color:#4ade80;")
            self._sidebar_discount.show()
        else:
            self._sidebar_discount.hide()
        self._sidebar_subtotal.setText(f"Subtotal: {fmt_currency(subtotal)}")
        self._sidebar_subtotal.setStyleSheet("font-weight:700; color:#c9a84c;")

    def _show_errors(self, errors: list) -> None:
        while self._error_layout.count():
            item = self._error_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not errors:
            self._error_box.hide()
            return
        for err in errors:
            label = QLabel(f"• {err}")
            label.setObjectName("errorText")
            self._error_layout.addWidget(label)
        self._error_box.show()

    def _continue(self) -> None:
        total_guests = self._adults_spin.value() + self._seniors_spin.value() + self._children_spin.value()
        errors = []
        if total_guests < MIN_GUESTS:
            errors.append(f"Minimum {MIN_GUESTS} guests required per booking.")
        if not self._name_input.text().strip():
            errors.append("Guest name is required.")
        if not self._contact_input.text().strip():
            errors.append("Contact number is required.")
        if not self._email_input.text().strip():
            errors.append("Email address is required.")

        self._show_errors(errors)
        if errors:
            return

        booking = dict(
            room=self._room,
            pricingMode=self._mode(),
            duration=self._duration_spin.value(),
            guests=dict(
                adults=self._adults_spin.value(),
                seniors=self._seniors_spin.value(),
                children=self._children_spin.value(),
            ),
            customer=dict(
                name=self._name_input.text().strip(),
                contact=self._contact_input.text().strip(),
                email=self._email_input.text().strip(),
                mop=self._mop_input.text().strip(),
                account=self._account_input.text().strip(),
            ),
            dining=[],
            extraServices=[],
        )
        self.go("dining", booking=booking)
