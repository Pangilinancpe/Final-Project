
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class BaseView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def on_enter(self, payload: dict) -> None:
        """Override to receive data from whichever view navigated here."""

    def on_show(self) -> None:
        """Override for anything that should run every time this view appears."""

    def on_leave(self) -> None:
        """Override for cleanup needed when navigating away from this view."""

    def go(self, view_name: str, **payload) -> None:
        """Convenience wrapper: self.go('rooms', tier_filter='Premium')."""
        self.navigate_to.emit(view_name, payload)
