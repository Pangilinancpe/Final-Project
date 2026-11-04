"""views/receipt_view.py — confirmation screen: the itemised receipt (with pictures), print, and done."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QVBoxLayout

from config import COLORS, HOTEL_HOTLINE, HOTEL_LOCATION, HOTEL_NAME, PAYMENT_LABELS, TIER_COLORS
from utils import CoverImage, button, clear_layout, divider, fmt_currency, label, load_pixmap, load_service_image, thumb
from views.base_view import BaseView
from views.payment_view import compute_totals

GOLD, GREEN, CENTER = COLORS["gold"], COLORS["green"], Qt.AlignmentFlag.AlignCenter
FONT = 16  # receipt text size in px
GOLD_BOLD = f"color:{GOLD}; font-weight:700; font-size:{FONT + 1}px;"


def line_row(left: str, right: str = "", style: str = "", picture=None) -> QHBoxLayout:
    """One receipt line: [optional small picture] description on the left, amount on the right."""
    style = f"font-size:{FONT}px;" + style
    row = QHBoxLayout()
    row.setContentsMargins(0, 3, 0, 3)
    if picture is not None:
        pic = label()
        pic.setPixmap(thumb(picture, 44))
        row.addWidget(pic)
    row.addWidget(label(left, style=style, wrap=True), 1)
    row.addWidget(label(right, style=style, wrap=True, align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
    return row


class ReceiptView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        outer = self.make_page()

        self._card = QFrame()
        self._card.setObjectName("card")
        self._card.setMaximumWidth(660)
        self._content = QVBoxLayout(self._card)
        self._content.setContentsMargins(28, 24, 28, 24)
        self._content.setSpacing(4)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(button("🖨  Print / Save PDF", "ghostButton", self._print))
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
        t, room, guests, cust, payer, pay = compute_totals(b), b["room"], b["guests"], b["customer"], b["payer"], b["payment"]
        row = lambda *args, **kw: c.addLayout(line_row(*args, **kw))
        section = lambda title: (c.addSpacing(4), c.addWidget(divider()), c.addSpacing(4), row(title, "", GOLD_BOLD))
        plural = "s" if b["duration"] > 1 else ""

        # header with the room picture
        banner = CoverImage(170)
        banner.set_pixmap(load_pixmap(room["image"], TIER_COLORS[room["tier"]], fallback=room["imageUrl"]))
        c.addWidget(banner)
        c.addSpacing(6)
        c.addWidget(label(HOTEL_NAME, style=f"font-size:28px; font-weight:800; color:{GOLD};", align=CENTER))
        c.addWidget(label(f"{HOTEL_LOCATION}  ·  Hotline: {HOTEL_HOTLINE}", style=f"font-size:{FONT - 2}px; color:{COLORS['muted']};", align=CENTER))
        c.addSpacing(6)
        c.addWidget(label("BOOKING RECEIPT", style="font-size:20px; font-weight:700;", align=CENTER))
        c.addWidget(label("✔ Transaction confirmed", style=f"font-size:{FONT}px; font-weight:600; color:{GREEN};", align=CENTER))
        row("Reference No.", b["reference"], f"color:{GOLD}; font-weight:700;")
        row("Date", b["createdAt"].strftime("%B %d, %Y  %I:%M %p"))

        section("GUEST DETAILS")
        for i, name in enumerate(b["guestNames"], 1):
            row(f"Guest {i}", name)
        row("Total guests", f"{sum(guests.values())} ({', '.join(f'{k.capitalize()}: {n}' for k, n in guests.items() if n)})")
        if b["childAges"]:
            row("Children's ages", ", ".join(f"{a} yrs" for a in b["childAges"]))
        row("Contact no.", cust["contact"])
        row("Email", cust["email"])

        section("PAYER")
        row("Name", payer["name"])
        row("Contact no.", payer["contact"])

        section("STAY")
        row("Room", f"{room['name']} ({room['tier']})")
        row("Length of stay", f"{b['duration']} {b['pricingMode']}{plural}")

        section("PAYMENT")
        row("Payment method", PAYMENT_LABELS[pay["method"]])
        for caption, key in (("E-wallet", "provider"), ("Account name", "accountName"), ("Account / reference no.", "accountRef")):
            if pay.get(key):
                row(caption, pay[key])

        section("CHARGES")
        row(f"Room ({b['duration']} {b['pricingMode']}{plural})", fmt_currency(t["base"]))
        if t["has_discount"]:
            row("Family Discount (10%)", f"−{fmt_currency(t['discount'])}", f"color:{GREEN};")
        for entry in b["dining"]:
            row(f"{entry['item']['name']} × {entry['qty']}", fmt_currency(entry["item"]["price"] * entry["qty"]))
        for entry in b["extraServices"]:
            row(f"{entry['item']['name']} × {entry['qty']}", fmt_currency(entry["item"]["price"] * entry["qty"]),
                picture=load_service_image(entry["item"]["image"]))

        c.addSpacing(4)
        c.addWidget(divider())
        row("TOTAL AMOUNT DUE", fmt_currency(t["grand_total"]), f"font-weight:800; font-size:21px; color:{GOLD};")
        c.addSpacing(8)
        c.addWidget(label("Saved to the booking records. Thank you for staying with us!", style=f"font-size:{FONT - 1}px; color:{COLORS['muted']};", align=CENTER))

    def _print(self) -> None:
        """Print the receipt (choose 'Microsoft Print to PDF' in the dialog to save it as a PDF)."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        if not QPrintDialog(printer, self).exec():
            return
        page = printer.pageRect(QPrinter.Unit.DevicePixel)
        scale = min(page.width() / self._card.width(), page.height() / self._card.height())
        painter = QPainter(printer)
        painter.scale(scale, scale)
        self._card.render(painter)
        painter.end()
        QMessageBox.information(self, "Print", "The receipt was sent to the printer.")
