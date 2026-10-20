from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, QLabel,
                             QLineEdit, QSpinBox, QComboBox, QPushButton)
from config import FAMILY_DISCOUNT as familyDiscount, MIN_GUESTS as minGuests # di pa sure about this
from utils import fmt_currency as fmtCurrency # bien yung utility functions (ftmCurrency ikaw na bahala kung ibahin mo)
from .base_view import BaseView # naka base toh kung ano nakalagay sa doc

rateKeys = ("perDay", "perHour")  # mag-iiba kung ano nasa data.py
units = ("day", "hour")
defaults = {"duration": 1, "adults": 2, "seniors": 0, "children": 0}
guestKeys = ("adults", "seniors", "children")


class BookingView(BaseView):
    def __init__(self):
        super().__init__()
        self.room = {}
        self.mode = QComboBox()
        self.mode.addItems(["Per Day", "Per Hour"])
        self.durationLabel = QLabel()
        self.spins = {key: QSpinBox() for key in defaults}
        self.fields = {key: QLineEdit() for key in ("name", "contact", "email")}
        for key, spin in self.spins.items():
            spin.setRange(1 if key == "duration" else 0, 365 if key == "duration" else 20)
            spin.valueChanged.connect(self.updateSummary)
        self.mode.currentIndexChanged.connect(self.updateSummary)

        form = QFormLayout()
        form.addRow("Rate", self.mode)
        form.addRow(self.durationLabel, self.spins["duration"])
        for key in guestKeys:
            form.addRow(key.title(), self.spins[key])
        for key, field in self.fields.items():
            form.addRow(key.title(), field)

        self.error = QLabel()
        self.error.setStyleSheet("background:#5c1a1a; color:#ffb4b4; padding:8px; border-radius:6px;")
        self.error.hide()

        backBtn, nextBtn = QPushButton("Back"), QPushButton("Next")
        backBtn.clicked.connect(lambda: self.go("rooms", {}))
        nextBtn.clicked.connect(self.onNext)
        buttons = QHBoxLayout()
        buttons.addWidget(backBtn)
        buttons.addStretch()
        buttons.addWidget(nextBtn)

        left = QVBoxLayout()
        left.addWidget(QLabel("Step 1 of 4: Who's staying?"))
        left.addLayout(form)
        left.addWidget(self.error)
        left.addStretch()
        left.addLayout(buttons)

        self.summary = QLabel()
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(300)
        QVBoxLayout(card).addWidget(self.summary)

        root = QHBoxLayout(self)
        root.addLayout(left, 1)
        root.addWidget(card)

    def on_enter(self, data):
        self.room = data["room"]
        self.mode.setCurrentIndex(0)
        for key, value in defaults.items():
            self.spins[key].setValue(value)
        for field in self.fields.values():
            field.clear()
        self.error.hide()
        self.updateSummary()

    def updateSummary(self):
        unit = units[self.mode.currentIndex()]
        count = self.spins["duration"].value()
        rate = self.room[rateKeys[self.mode.currentIndex()]]
        subtotal = rate * count
        hasFamily = self.spins["seniors"].value() or self.spins["children"].value()
        discount = subtotal * familyDiscount if hasFamily else 0

        self.durationLabel.setText(f"{unit.title()}s")
        lines = [self.room["name"], f"{fmtCurrency(rate)} x {count} {unit}(s)"]
        if discount:
            lines.append(f"Family discount: -{fmtCurrency(discount)}")
        lines.append(f"Total: {fmtCurrency(subtotal - discount)}")
        self.summary.setText("\n".join(lines))

    def onNext(self):
        guests = sum(self.spins[key].value() for key in guestKeys)
        texts = {key: field.text().strip() for key, field in self.fields.items()}
        if guests < minGuests:
            return self.showError(f"Need at least {minGuests} guests.")
        if not all(texts.values()):
            return self.showError("Fill in your name, contact and email.")

        self.error.hide()
        values = {key: spin.value() for key, spin in self.spins.items()}
        self.go("dining", {"room": self.room, "mode": units[self.mode.currentIndex()], **values, **texts})

    def showError(self, message):
        self.error.setText(message)
        self.error.show()