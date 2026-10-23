import faulthandler
import sys
import traceback

from PyQt6.QtCore import qInstallMessageHandler
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from config import APP_SUBTITLE, APP_TITLE, WINDOW_MIN_SIZE
from styles import QSS_STYLE
from views import (BookingView, DiningView, HomeView, PaymentView, ReceiptView,
                   RoomDetailView, RoomsView, ServicesView)
from widgets import NavBar


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

        # Every screen is created once; on_enter() refreshes it with new data on each visit.
        self.views = {
            "home": HomeView(), "rooms": RoomsView(), "room_detail": RoomDetailView(),
            "booking": BookingView(), "dining": DiningView(), "services": ServicesView(),
            "payment": PaymentView(), "receipt": ReceiptView(),
        }
        for view in self.views.values():
            view.navigate_to.connect(self._navigate)
            self.stack.addWidget(view)
        self._navigate("home", {})

    def _navigate(self, name: str, payload: dict) -> None:
        if name not in self.views:
            return
        self.stack.currentWidget().on_leave()
        view = self.views[name]
        view.on_enter(payload)
        self.stack.setCurrentWidget(view)
        view.on_show()


def main() -> None:
    # PyQt6 aborts the whole process (exit code 0xC0000409) on an unhandled error inside a Qt callback.
    # A custom hook prints the traceback and keeps the app alive.
    sys.excepthook = lambda *exc: traceback.print_exception(*exc)
    faulthandler.enable()  # on a hard crash, prints which Python line was running
    qInstallMessageHandler(lambda _mode, _ctx, msg: print("Qt:", msg, file=sys.stderr))
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
