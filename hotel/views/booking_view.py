"""views/booking_view.py — Step 1 of 4: stay, guests (first / M.I. / last / suffix, children's ages), contacts and the payer."""

import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QWidget

from config import MAX_GUESTS, MIN_GUESTS
from utils import button, clear_layout, error_box, fmt_currency, label, sidebar_card, valid_phone
from views.base_view import BaseView
from views.payment_view import compute_totals
from widgets import NameRow

UNITS = ("day", "hour")
GUESTS = {"adults": ("Adults", 1), "seniors": ("Seniors", 0), "children": ("Children (under 18)", 0)}  # key: (caption, default)
FIELD_W, SMALL_W, FORM_W, CAPTION_W = 420, 200, 640, 130  # widest a text box / small box / the whole form may grow, so full screen stays tidy


def _caption(text) -> QLabel:
    lab = label(text)
    lab.setMinimumWidth(CAPTION_W)
    return lab


def _edit(placeholder: str) -> QLineEdit:
    field = QLineEdit()
    field.setPlaceholderText(placeholder)
    field.setMaximumWidth(FIELD_W)
    return field


class BookingView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.room, self.name_rows, self.age_spins = {}, [], []
        self.mode = QComboBox()
        self.mode.addItems(["Per Day", "Per Hour"])
        self.duration = QSpinBox()
        self.duration.setRange(1, 365)
        self.duration_label = label("Days")
        self.spins = {k: QSpinBox() for k in GUESTS}
        for box in (self.mode, self.duration, *self.spins.values()):
            box.setMaximumWidth(SMALL_W)
        self.contact, self.email = _edit("e.g. 0917 123 4567"), _edit("name@example.com")
        self.payer_name, self.payer_contact = NameRow("the person paying"), _edit("e.g. 0917 123 4567")
        self.names_box, self.ages_box = QVBoxLayout(), QVBoxLayout()  # filled by _sync(): one row per guest / child

        self.duration.valueChanged.connect(self.update_summary)
        self.mode.currentIndexChanged.connect(self.update_summary)
        for spin in self.spins.values():
            spin.valueChanged.connect(self._sync)

        stay, guests, contact, payer = QFormLayout(), QFormLayout(), QFormLayout(), QFormLayout()
        stay.addRow(_caption("Rate"), self.mode)
        self.duration_label.setMinimumWidth(CAPTION_W)
        stay.addRow(self.duration_label, self.duration)
        for key, (caption, _default) in GUESTS.items():
            guests.addRow(_caption(caption), self.spins[key])
        contact.addRow(_caption("Contact no."), self.contact)
        contact.addRow(_caption("Email"), self.email)
        payer.addRow(_caption("Payer contact no."), self.payer_contact)

        self._hint = label(muted=True, wrap=True)
        self._error_box, self.error = error_box()
        left = QVBoxLayout()
        left.setSpacing(8)
        left.addWidget(label("STEP 1 OF 4", "sectionKicker"))
        left.addWidget(label("Who's staying?", "sectionTitle"))
        for heading, body in (("STAY", stay), ("GUESTS", None), ("GUEST CONTACT", contact), ("PAYER (the person paying)", payer)):
            left.addSpacing(6)
            left.addWidget(label(heading, "sectionKicker"))
            if body is None:
                left.addWidget(self._hint)
                left.addLayout(guests)
                left.addLayout(self.names_box)
                left.addLayout(self.ages_box)
            elif body is payer:
                left.addWidget(label("Payer name", muted=True))
                left.addWidget(self.payer_name)
                left.addLayout(body)
            else:
                left.addLayout(body)
        left.addWidget(self._error_box)
        left.addWidget(button("Next: Dining →", "primaryButton", self.on_next), alignment=Qt.AlignmentFlag.AlignRight)
        left.addStretch(1)

        form = QWidget()  # the form never gets wider than FORM_W, even when the window is maximised
        form.setLayout(left)
        form.setMaximumWidth(FORM_W)

        card, lay = sidebar_card("Booking Summary", 300)
        self.summary = label(muted=True, wrap=True)
        lay.addWidget(self.summary)
        lay.addStretch(1)

        outer = self.make_page(back=lambda: self.go("rooms"), cancel=True)
        row = QHBoxLayout()
        row.setSpacing(24)
        row.addStretch(1)
        row.addWidget(form, 4)
        row.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        row.addStretch(1)
        self.add_scroll(outer, row)

    # ----- screen lifecycle -----
    def on_enter(self, payload: dict) -> None:
        if payload.get("room") is None:
            return
        saved = payload.get("booking")  # present when coming back from the dining step
        self.room = payload["room"]
        self.mode.setCurrentIndex(1 if saved and saved["pricingMode"] == "hour" else 0)
        self.duration.setValue(saved["duration"] if saved else 1)
        self.name_rows, self.age_spins = [], []  # start from empty boxes
        for spin in self.spins.values():
            spin.setMaximum(MAX_GUESTS)
            spin.setValue(0)
        for key, spin in self.spins.items():
            spin.setValue(saved["guests"][key] if saved else GUESTS[key][1])
        self._sync()
        values = [saved["customer"]["contact"], saved["customer"]["email"], saved["payer"]["contact"]] if saved else [""] * 3
        for field, value in zip((self.contact, self.email, self.payer_contact), values):
            field.setText(value)
        self.payer_name.set_parts(saved["payer"].get("parts", {}) if saved else {})
        if saved:
            for row, parts in zip(self.name_rows, saved.get("guestParts", [])):
                row.set_parts(parts)
            for spin, age in zip(self.age_spins, saved["childAges"]):
                spin.setValue(age)
        self._error_box.hide()

    def _limit(self) -> int:
        return min(MAX_GUESTS, self.room.get("maxGuests", MAX_GUESTS))

    def _sync(self) -> None:
        """Keep the total within the limit, one name row per guest and one 'age' box per child."""
        counts = {k: s.value() for k, s in self.spins.items()}
        total = sum(counts.values())
        for key, spin in self.spins.items():
            spin.setMaximum(max(counts[key], self._limit() - (total - counts[key])))
        self._hint.setText(f"Maximum {self._limit()} guests for this room. Enter the name of every guest "
                           "(middle initial and suffix are optional).")

        kept, ages = [r.parts() for r in self.name_rows], [s.value() for s in self.age_spins]
        clear_layout(self.names_box)
        clear_layout(self.ages_box)
        self.name_rows, self.age_spins = [], []
        for i in range(total):
            row = NameRow(f"guest {i + 1}")
            if i < len(kept):
                row.set_parts(kept[i])
            self.names_box.addWidget(label(f"Guest {i + 1}", style="font-weight:600;"))
            self.names_box.addWidget(row)
            self.name_rows.append(row)
        for i in range(counts["children"]):
            spin = QSpinBox()
            spin.setRange(0, 17)
            spin.setSuffix(" years old")
            spin.setMaximumWidth(SMALL_W)
            spin.setValue(ages[i] if i < len(ages) else 0)
            self.ages_box.addWidget(label(f"Child {i + 1} age", muted=True))
            self.ages_box.addWidget(spin)
            self.age_spins.append(spin)
        self.update_summary()

    def _booking(self) -> dict:
        """The booking dict every later screen builds on (same shape compute_totals expects)."""
        names = [r.text() for r in self.name_rows]
        return dict(
            room=self.room, pricingMode=UNITS[self.mode.currentIndex()], duration=self.duration.value(),
            guests={k: s.value() for k, s in self.spins.items()}, guestNames=names, guestParts=[r.parts() for r in self.name_rows],
            childAges=[s.value() for s in self.age_spins],
            customer=dict(name=names[0] if names else "", contact=self.contact.text().strip(), email=self.email.text().strip()),
            payer=dict(name=self.payer_name.text(), parts=self.payer_name.parts(), contact=self.payer_contact.text().strip()),
            dining=[], extraServices=[],
        )

    def update_summary(self) -> None:
        if not self.room:
            return
        b = self._booking()
        totals, unit = compute_totals(b), b["pricingMode"]
        rate = self.room["pricePerDay" if unit == "day" else "pricePerHour"]
        self.duration_label.setText(f"{unit.title()}s")
        lines = [self.room["name"], f"{fmt_currency(rate)} × {b['duration']} {unit}(s)", f"Guests: {sum(b['guests'].values())}"]
        if totals["has_discount"]:
            lines.append(f"Family discount: −{fmt_currency(totals['discount'])}")
        lines.append(f"Total: {fmt_currency(totals['room_total'])}")
        self.summary.setText("\n".join(lines))

    # ----- validation -----
    def on_next(self) -> None:
        b = self._booking()
        total, c, p = len(self.name_rows), b["customer"], b["payer"]
        if total < MIN_GUESTS:
            return self._show_error(f"Add at least {MIN_GUESTS} guest.")
        if total > self._limit():
            return self._show_error(f"Only {self._limit()} guests are allowed for this room.")
        for row in self.name_rows:
            if row.error():
                return self._show_error(row.error())
        if not valid_phone(c["contact"]):
            return self._show_error("Enter a valid guest contact number (10 to 12 digits).")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c["email"]):
            return self._show_error("Enter a valid email address.")
        if self.payer_name.error():
            return self._show_error(self.payer_name.error())
        if not valid_phone(p["contact"]):
            return self._show_error("Enter a valid contact number for the payer (10 to 12 digits).")
        self._error_box.hide()
        self.go("dining", booking=b)

    def _show_error(self, message: str) -> None:
        self.error.setText(message)
        self._error_box.show()
