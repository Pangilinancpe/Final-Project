"""views/records_view.py — data management: every confirmed booking saved in the SQLite database (hotel.db)."""

from PyQt6.QtWidgets import (QAbstractItemView, QFileDialog, QHBoxLayout, QHeaderView, QMessageBox, QTableWidget,
                             QTableWidgetItem)

import database
from config import PAYMENT_LABELS
from utils import button, fmt_currency, label
from views.base_view import BaseView

COLUMNS = ("Reference", "Date", "Guests", "Room", "Stay", "Payment", "Total")


class RecordsView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []
        outer = self.make_page()
        outer.addWidget(label("DATA MANAGEMENT", "sectionKicker"))
        outer.addWidget(label("Booking Records", "sectionTitle"))
        outer.addWidget(label(f"Every confirmed booking is saved in this file: {database.DB_PATH}", muted=True, wrap=True))

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        outer.addWidget(self.table, 1)
        self._empty = label("No bookings saved yet.", muted=True)
        outer.addWidget(self._empty)

        row = QHBoxLayout()
        row.addWidget(button("Delete selected", "dangerButton", self._delete))
        row.addWidget(button("Export to CSV", "ghostButton", self._export))
        row.addStretch(1)
        row.addWidget(button("← Back to home", "ghostButton", lambda: self.go("home")))
        outer.addLayout(row)

    def on_enter(self, payload: dict) -> None:
        self._reload()

    def _reload(self) -> None:
        self._rows = database.list_bookings()
        self.table.setRowCount(len(self._rows))
        self._empty.setVisible(not self._rows)
        for r, b in enumerate(self._rows):
            cells = (b["reference"], b["created_at"].replace("T", " ")[:16], b["guest_names"] or "",
                     f"{b['room_name']} ({b['room_tier']})", f"{b['duration']} {b['pricing_mode']}(s)",
                     PAYMENT_LABELS.get(b["payment_method"], b["payment_method"]), fmt_currency(b["grand_total"]))
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QTableWidgetItem(text))

    def _delete(self) -> None:
        r = self.table.currentRow()
        if r < 0:
            return QMessageBox.information(self, "Delete booking", "Select a booking in the table first.")
        ref = self._rows[r]["reference"]
        if QMessageBox.question(self, "Delete booking", f"Delete booking {ref} from the records?") == QMessageBox.StandardButton.Yes:
            database.delete_booking(ref)
            self._reload()

    def _export(self) -> None:
        """Save all bookings to a .csv file the guest/teacher can open in Excel."""
        if not self._rows:
            return QMessageBox.information(self, "Export", "There are no bookings to export yet.")
        path, _ = QFileDialog.getSaveFileName(self, "Save bookings", "bookings.csv", "CSV file (*.csv)")
        if not path:
            return
        try:
            count = database.export_csv(path)
        except OSError as exc:
            return QMessageBox.critical(self, "Could not save", f"The file could not be saved:\n{exc}")
        QMessageBox.information(self, "Export", f"Saved {count} booking(s) to:\n{path}")
