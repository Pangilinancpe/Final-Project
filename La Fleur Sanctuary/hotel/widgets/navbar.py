"""widgets/navbar.py — top bar shown above every view. Emits signals; main.py decides what they do."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from config import APP_TITLE, HOTEL_HOTLINE
from utils import button, label


class NavBar(QFrame):
    home_clicked = pyqtSignal()
    rooms_clicked = pyqtSignal()
    book_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(64)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(16)

        lay.addWidget(button(f"🏠  {APP_TITLE}", "brandButton", self.home_clicked))
        lay.addStretch(1)
        lay.addWidget(button("Rooms", "linkButton", self.rooms_clicked))
        for text in ("·", "Manila, PH", "·", f"Hotline: {HOTEL_HOTLINE}"):
            lay.addWidget(label(text, muted=True))
        lay.addStretch(1)
        lay.addWidget(button("Book a Room", "primaryButton", self.book_clicked))
