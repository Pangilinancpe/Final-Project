# Demo for services_view.py (should show what it looks like)
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from views.services_view import ServicesView

from config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from styles import QSS_STYLE


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS_STYLE)
    view = ServicesView()
    view.setWindowTitle(f"{APP_TITLE} • Services preview")
    view.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    view.on_enter({"guest": {"name": "Sample Guest"}, "dining": {}})

    def show_destination(destination, data):
        QMessageBox.information(
            view, "Navigation preview",
            f"Destination: {destination}\n\nBooking data:\n{data}"
        )

    view.navigate_to.connect(show_destination)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

