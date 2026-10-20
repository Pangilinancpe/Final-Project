from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class BaseView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def go(self, destination, data):
        self.navigate_to.emit(destination, data)

    def on_enter(self, data=None):
        pass

    def on_show(self):
        pass

    def on_leave(self):
        pass