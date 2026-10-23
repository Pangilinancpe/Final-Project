"""views/booking_view.py — Step 1 of 4: rate, duration, guests and contact details."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QSpinBox, QVBoxLayout

from config import MAX_GUESTS_SPIN, MIN_GUESTS
from utils import button, fmt_currency, label, sidebar_card
from views.base_view import BaseView
from views.payment_view import compute_totals

UNITS = ("day", "hour")
GUESTS = {"adults": ("Adults", 2), "seniors": ("Seniors", 0), "children": ("Children", 0)}  # key: (caption, default)
FIELDS = ("name", "contact", "email")


class BookingView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.room = {}
        self.mode = QComboBox()
        self.mode.addItems(["Per Day", "Per Hour"])
        self.duration = QSpinBox()
        self.duration.setRange(1, 365)
        self.duration_label = label("Days")
        self.spins = {k: QSpinBox() for k in GUESTS}
        self.fields = {k: QLineEdit() for k in FIELDS}
        for spin in self.spins.values():
            spin.setRange(0, MAX_GUESTS_SPIN)
        for spin in (self.duration, *self.spins.values()):
            spin.valueChanged.connect(self.update_summary)
        self.mode.currentIndexChanged.connect(self.update_summary)

        form = QFormLayout()
        form.setVerticalSpacing(10)
        form.addRow("Rate", self.mode)
        form.addRow(self.duration_label, self.duration)
        for key, (caption, _default) in GUESTS.items():
            form.addRow(caption, self.spins[key])
        for key, field in self.fields.items():
            form.addRow(key.title(), field)

        self.error = label(name="errorText", wrap=True)
        self._error_box = QFrame()
        self._error_box.setObjectName("errorBox")
        QVBoxLayout(self._error_box).addWidget(self.error)
        self._error_box.hide()

        buttons = QHBoxLayout()
        buttons.addWidget(button("← Back", "ghostButton", lambda: self.go("rooms")))
        buttons.addStretch(1)
        buttons.addWidget(button("✕ Cancel booking", "ghostButton", self._cancel))
        buttons.addWidget(button("Next: Dining →", "primaryButton", self.on_next))

        left = QVBoxLayout()
        left.addWidget(label("STEP 1 OF 4", "sectionKicker"))
        left.addWidget(label("Who's staying?", "sectionTitle"))
        left.addLayout(form)
        left.addWidget(self._error_box)
        left.addStretch(1)
        left.addLayout(buttons)

        card, lay = sidebar_card("Booking Summary", 300)
        self.summary = label(muted=True, wrap=True)
        lay.addWidget(self.summary)
        lay.addStretch(1)

        root = QHBoxLayout(self)
        root.setContentsMargins(48, 24, 48, 24)
        root.setSpacing(24)
        root.addLayout(left, 1)
        root.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)

    def on_enter(self, payload: dict) -> None:
        if payload.get("room") is None:
            return
        saved = payload.get("booking")  # present when coming back from the dining step
        self.room = payload["room"]
        self.mode.setCurrentIndex(1 if saved and saved["pricingMode"] == "hour" else 0)
        self.duration.setValue(saved["duration"] if saved else 1)
        for key, spin in self.spins.items():
            spin.setValue(saved["guests"][key] if saved else GUESTS[key][1])
        for key, field in self.fields.items():
            field.setText(saved["customer"][key] if saved else "")
        self._error_box.hide()
        self.update_summary()

    def _booking(self) -> dict:
        """The booking dict every later screen builds on (same shape compute_totals expects)."""
        return dict(
            room=self.room, pricingMode=UNITS[self.mode.currentIndex()], duration=self.duration.value(),
            guests={k: s.value() for k, s in self.spins.items()},
            customer={k: f.text().strip() for k, f in self.fields.items()},
            dining=[], extraServices=[],
        )

    def update_summary(self) -> None:
        if not self.room:
            return
        b = self._booking()
        totals, unit = compute_totals(b), b["pricingMode"]
        rate = self.room["pricePerDay" if unit == "day" else "pricePerHour"]
        self.duration_label.setText(f"{unit.title()}s")
        lines = [self.room["name"], f"{fmt_currency(rate)} × {b['duration']} {unit}(s)"]
        if totals["has_discount"]:
            lines.append(f"Family discount: −{fmt_currency(totals['discount'])}")
        lines.append(f"Total: {fmt_currency(totals['room_total'])}")
        self.summary.setText("\n".join(lines))

    def on_next(self) -> None:
        b = self._booking()
        guests, customer = sum(b["guests"].values()), b["customer"]
        if guests < MIN_GUESTS:
            return self._show_error(f"Need at least {MIN_GUESTS} guests.")
        if guests > self.room["maxGuests"]:
            return self._show_error(f"This room fits at most {self.room['maxGuests']} guests.")
        if not all(customer.values()):
            return self._show_error("Fill in your name, contact and email.")
        if "@" not in customer["email"]:
            return self._show_error("Please enter a valid email address.")
        self._error_box.hide()
        self.go("dining", booking=b)

    def _show_error(self, message: str) -> None:
        self.error.setText(message)
        self._error_box.show()
