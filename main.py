import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget

from config import APP_TITLE, APP_SUBTITLE, WINDOW_MIN_SIZE
from styles import QSS_STYLE
from widgets import NavBar
from views import (
    HomeView, RoomsView, RoomDetailView, BookingView,
    DiningView, ServicesView, PaymentView, ReceiptView,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} — {APP_SUBTITLE}")
        self.resize(*WINDOW_MIN_SIZE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.navbar = NavBar()
        self.navbar.home_clicked.connect(lambda: self._navigate("home", {}))
        self.navbar.rooms_clicked.connect(lambda: self._navigate("rooms", {}))
        self.navbar.book_clicked.connect(lambda: self._navigate("rooms", {}))
        layout.addWidget(self.navbar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Registry: view name -> page instance. Every screen is created once
        # and reused — on_enter() refreshes it with new data each visit.
        self.views = {
            "home": HomeView(),
            "rooms": RoomsView(),
            "room_detail": RoomDetailView(),
            "booking": BookingView(),
            "dining": DiningView(),
            "services": ServicesView(),
            "payment": PaymentView(),
            "receipt": ReceiptView(),
        }
        for view in self.views.values():
            view.navigate_to.connect(self._navigate)
            self.stack.addWidget(view)

        self._navigate("home", {})

    def _navigate(self, view_name: str, payload: dict) -> None:
        if view_name not in self.views:
            return
        current = self.stack.currentWidget()
        if current is not None:
            current.on_leave()
        view = self.views[view_name]
        view.on_enter(payload)
        self.stack.setCurrentWidget(view)
        view.on_show()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
