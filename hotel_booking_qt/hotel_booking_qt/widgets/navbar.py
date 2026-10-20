-"""
widgets/navbar.py
Top navigation bar, shown above every view. Equivalent of the React
<NavBar/> component — emits Qt signals instead of taking callback props, so
main.py (the only place that owns the QStackedWidget) decides what each
click actually does.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from config import APP_TITLE, HOTEL_HOTLINE


class NavBar(QFrame):
    home_clicked = pyqtSignal()
    rooms_clicked = pyqtSignal()
    book_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        brand = QPushButton(f"🏠  {APP_TITLE}")
        brand.setObjectName("brandButton")
        brand.setCursor(Qt.CursorShape.PointingHandCursor)
        brand.setFlat(True)
        brand.clicked.connect(self.home_clicked.emit)
        layout.addWidget(brand)

        layout.addStretch(1)

        rooms_link = QPushButton("Rooms")
        rooms_link.setObjectName("linkButton")
        rooms_link.setCursor(Qt.CursorShape.PointingHandCursor)
        rooms_link.setFlat(True)
        rooms_link.clicked.connect(self.rooms_clicked.emit)
        layout.addWidget(rooms_link)

        layout.addWidget(self._muted_label("·"))
        layout.addWidget(self._muted_label("Manila, PH"))
        layout.addWidget(self._muted_label("·"))
        layout.addWidget(self._muted_label(f"Hotline: {HOTEL_HOTLINE}"))

        layout.addStretch(1)

        book_btn = QPushButton("Book a Room")
        book_btn.setObjectName("primaryButton")
        book_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        book_btn.clicked.connect(self.book_clicked.emit)
        layout.addWidget(book_btn)

    @staticmethod
    def _muted_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("class", "muted")
        return label
