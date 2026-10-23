from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QScrollArea, QVBoxLayout, QWidget

from utils import button


class BaseView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def on_enter(self, payload: dict) -> None:
        """Override to receive data from whichever view navigated here."""

    def on_show(self) -> None:
        """Override for anything that should run every time this view appears."""

    def on_leave(self) -> None:
        """Override for cleanup when navigating away."""

    def go(self, view_name: str, **payload) -> None:
        """self.go('rooms', tier_filter='Suite')"""
        self.navigate_to.emit(view_name, payload)

    def make_page(self, back=None, margins=(48, 24, 48, 24), cancel=False) -> QVBoxLayout:
        """Padded outer layout, with an optional '← Back' button (and '✕ Cancel booking' if cancel=True) on top."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(*margins)
        outer.setSpacing(14)
        if back:
            top = QHBoxLayout()
            top.addWidget(button("← Back", "ghostButton", back))
            top.addStretch(1)
            if cancel:
                top.addWidget(button("✕ Cancel booking", "ghostButton", self._cancel))
            outer.addLayout(top)
        return outer

    def _cancel(self) -> None:
        """Ask for confirmation, then abandon the booking and return to the main (home) view."""
        answer = QMessageBox.question(self, "Cancel booking", "Cancel this booking and return to the main page?\n"
                                      "Everything you entered will be cleared.")
        if answer == QMessageBox.StandardButton.Yes:
            self.go("home")

    @staticmethod
    def add_scroll(outer: QVBoxLayout, layout) -> None:
        """Add a scroll area to `outer` whose content is `layout` (a layout not yet attached to anything)."""
        scroll, body = QScrollArea(), QWidget()
        scroll.setWidgetResizable(True)
        body.setLayout(layout)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)
