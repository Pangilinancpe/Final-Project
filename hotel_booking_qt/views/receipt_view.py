
import random
import string
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from config import HOTEL_HOTLINE, HOTEL_LOCATION, HOTEL_NAME, PAYMENT_LABELS
from utils import fmt_currency
from views.base_view import BaseView
from views.payment_view import compute_totals


class ReceiptView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        self._body_layout = QVBoxLayout(body)
        self._body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._body_layout.setSpacing(12)

    def on_enter(self, payload: dict) -> None:
        booking = payload.get("booking")
        if booking is None:
            return
        self._booking = booking
        self._render_receipt()

    def _clear(self) -> None:
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _render_receipt(self) -> None:
        self._clear()
        booking = self._booking
        totals = compute_totals(booking)
        ref = "ME-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        now = datetime.now().strftime("%B %d, %Y · %I:%M %p")

        check = QLabel("✓")
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check.setStyleSheet(
            "color:#c9a84c; font-size:22px; border:1px solid rgba(201,168,76,100);"
            "border-radius:28px; background-color:rgba(201,168,76,25);"
        )
        check.setFixedSize(56, 56)
        self._body_layout.addWidget(check, alignment=Qt.AlignmentFlag.AlignCenter)

        confirmed = QLabel("BOOKING CONFIRMED")
        confirmed.setObjectName("sectionKicker")
        confirmed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._body_layout.addWidget(confirmed)

        heading = QLabel("Booking Receipt")
        heading.setStyleSheet("font-size:22px; font-weight:600;")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._body_layout.addWidget(heading)

        self._body_layout.addWidget(self._build_card(booking, totals, ref, now))

        thanks = QLabel(f"Thank you for choosing {HOTEL_NAME.replace(' Hotel', '')}. We look forward to welcoming you.")
        thanks.setProperty("class", "muted")
        thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._body_layout.addWidget(thanks)

        btn_row = QHBoxLayout()
        print_btn = QPushButton("🖨 Print Receipt")
        print_btn.setObjectName("ghostButton")
        print_btn.clicked.connect(self._print_stub)
        done_btn = QPushButton("Done")
        done_btn.setObjectName("primaryButton")
        done_btn.clicked.connect(self._done)
        btn_row.addWidget(print_btn)
        btn_row.addWidget(done_btn)
        self._body_layout.addLayout(btn_row)

    def _build_card(self, booking: dict, totals: dict, ref: str, now: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        hotel_col = QVBoxLayout()
        hotel_name_label = QLabel(HOTEL_NAME.upper())
        hotel_name_label.setProperty("class", "muted")
        hotel_loc_label = QLabel(f"{HOTEL_LOCATION} · {HOTEL_HOTLINE}")
        hotel_loc_label.setProperty("class", "muted")
        hotel_col.addWidget(hotel_name_label)
        hotel_col.addWidget(hotel_loc_label)
        header_row.addLayout(hotel_col)
        header_row.addStretch(1)
        ref_col = QVBoxLayout()
        ref_label = QLabel("Ref No.")
        ref_label.setProperty("class", "muted")
        ref_value = QLabel(ref)
        ref_value.setStyleSheet("color:#c9a84c; font-weight:600;")
        ref_col.addWidget(ref_label)
        ref_col.addWidget(ref_value)
        header_row.addLayout(ref_col)
        layout.addLayout(header_row)

        g = booking["guests"]
        info_rows = [
            ("Guest Name", booking["customer"]["name"]),
            ("Contact", booking["customer"]["contact"]),
            ("Email", booking["customer"]["email"]),
            ("Date Issued", now),
            ("Payment Method", PAYMENT_LABELS.get(booking["payment"], "—")),
            ("Total Guests", f"{g['adults'] + g['seniors'] + g['children']} pax"),
        ]
        info_grid = QHBoxLayout()
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        for i, (label_text, value) in enumerate(info_rows):
            target = col1 if i % 2 == 0 else col2
            lbl = QLabel(label_text)
            lbl.setProperty("class", "muted")
            value_label = QLabel(str(value))
            target.addWidget(lbl)
            target.addWidget(value_label)
        info_grid.addLayout(col1)
        info_grid.addLayout(col2)
        layout.addLayout(info_grid)

        layout.addWidget(self._hline())

        room_kicker = QLabel("ROOM CHARGE")
        room_kicker.setProperty("class", "muted")
        layout.addWidget(room_kicker)

        room_row = QHBoxLayout()
        room_col = QVBoxLayout()
        room_name = QLabel(f"<b>{booking['room']['name']}</b>")
        room_name.setTextFormat(Qt.TextFormat.RichText)
        plural = "s" if booking["duration"] > 1 else ""
        room_meta = QLabel(f"{booking['room']['tier']} · {booking['duration']} {booking['pricingMode']}{plural}")
        room_meta.setProperty("class", "muted")
        room_col.addWidget(room_name)
        room_col.addWidget(room_meta)
        if totals["has_discount"]:
            discount_note = QLabel("Family discount (10%) applied")
            discount_note.setStyleSheet("color:#4ade80; font-size:11px;")
            room_col.addWidget(discount_note)
        room_row.addLayout(room_col)
        room_row.addStretch(1)

        price_col = QVBoxLayout()
        if totals["has_discount"]:
            strike = QLabel(fmt_currency(totals["base"]))
            strike.setStyleSheet("color:#7a8499; text-decoration: line-through; font-size:11px;")
            price_col.addWidget(strike, alignment=Qt.AlignmentFlag.AlignRight)
        room_price = QLabel(fmt_currency(totals["room_total"]))
        room_price.setStyleSheet("font-weight:700;")
        price_col.addWidget(room_price, alignment=Qt.AlignmentFlag.AlignRight)
        room_row.addLayout(price_col)
        layout.addLayout(room_row)

        if booking["dining"]:
            layout.addWidget(self._hline())
            dining_kicker = QLabel("ROOM SERVICE")
            dining_kicker.setProperty("class", "muted")
            layout.addWidget(dining_kicker)
            for d in booking["dining"]:
                line = QLabel(f"{d['item']['name']} ×{d['qty']} — {fmt_currency(d['item']['price'] * d['qty'])}")
                line.setProperty("class", "muted")
                layout.addWidget(line)

        if booking["extraServices"]:
            layout.addWidget(self._hline())
            svc_kicker = QLabel("ADDITIONAL SERVICES")
            svc_kicker.setProperty("class", "muted")
            layout.addWidget(svc_kicker)
            for s in booking["extraServices"]:
                line = QLabel(f"{s['item']['name']} ×{s['qty']} — {fmt_currency(s['item']['price'] * s['qty'])}")
                line.setProperty("class", "muted")
                layout.addWidget(line)

        layout.addWidget(self._hline())
        total_row = QHBoxLayout()
        total_label = QLabel("TOTAL AMOUNT DUE")
        total_label.setStyleSheet("font-weight:700;")
        total_value = QLabel(fmt_currency(totals["grand_total"]))
        total_value.setStyleSheet("font-size:20px; font-weight:800; color:#c9a84c;")
        total_row.addWidget(total_label)
        total_row.addStretch(1)
        total_row.addWidget(total_value)
        layout.addLayout(total_row)

        return card

    @staticmethod
    def _hline() -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        return divider

    def _print_stub(self) -> None:
        QMessageBox.information(self, "Print Receipt", "Printing isn't wired up in this demo yet.")

    def _done(self) -> None:
        self.go("home")
