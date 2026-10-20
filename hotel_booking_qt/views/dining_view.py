"""
views/dining_view.py
Step 2 of 4: room-service pre-order menu with a category filter and a live
order summary sidebar. Equivalent of the React <DiningView/>.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from data import DINING, find_dining_item
from utils import fmt_currency
from views.base_view import BaseView


class DiningView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking = None
        self._orders: dict = {}
        self._category = "All"
        self._qty_labels: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 24, 48, 24)
        outer.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghostButton")
        back_btn.clicked.connect(self._back)
        outer.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        row = QHBoxLayout(body)
        row.setSpacing(24)

        left = QVBoxLayout()
        kicker = QLabel("STEP 2 OF 4")
        kicker.setObjectName("sectionKicker")
        left.addWidget(kicker)
        title = QLabel("Room Service Menu")
        title.setObjectName("sectionTitle")
        left.addWidget(title)
        sub = QLabel("Pre-order dining for your stay. Items will be delivered to your room.")
        sub.setProperty("class", "muted")
        left.addWidget(sub)

        categories = ["All"] + sorted({d["category"] for d in DINING})
        self._cat_combo = QComboBox()
        self._cat_combo.addItems(categories)
        self._cat_combo.currentTextChanged.connect(self._on_category_changed)
        left.addWidget(self._cat_combo)

        self._items_host = QVBoxLayout()
        left.addLayout(self._items_host)
        left.addStretch(1)

        row.addLayout(left, 2)
        row.addWidget(self._build_sidebar(), 0, Qt.AlignmentFlag.AlignTop)

        self._rebuild_items()

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout(sidebar)
        layout.addWidget(self._bold("Dining Order"))

        self._order_lines_host = QVBoxLayout()
        layout.addLayout(self._order_lines_host)

        self._empty_label = QLabel("No items selected yet.")
        self._empty_label.setProperty("class", "muted")
        layout.addWidget(self._empty_label)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self._total_label = QLabel("Dining Total: ₱0")
        self._total_label.setStyleSheet("font-weight:700; color:#c9a84c;")
        layout.addWidget(self._total_label)

        continue_btn = QPushButton("Continue to Services →")
        continue_btn.setObjectName("primaryButton")
        continue_btn.clicked.connect(self._continue)
        layout.addWidget(continue_btn)

        skip_btn = QPushButton("Skip dining →")
        skip_btn.setObjectName("ghostButton")
        skip_btn.clicked.connect(self._skip)
        layout.addWidget(skip_btn)
        layout.addStretch(1)
        return sidebar

    @staticmethod
    def _bold(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight:600;")
        return label

    def on_enter(self, payload: dict) -> None:
        booking = payload.get("booking")
        if booking is None:
            return
        self._booking = booking
        self._orders = {}
        self._rebuild_items()
        self._refresh_sidebar()

    def _on_category_changed(self, text: str) -> None:
        self._category = text
        self._rebuild_items()

    def _rebuild_items(self) -> None:
        while self._items_host.count():
            item = self._items_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._qty_labels = {}

        items = DINING if self._category == "All" else [d for d in DINING if d["category"] == self._category]
        for item in items:
            self._items_host.addWidget(self._item_row(item))

    def _item_row(self, item: dict) -> QFrame:
        row_frame = QFrame()
        layout = QHBoxLayout(row_frame)
        layout.setContentsMargins(0, 6, 0, 6)

        text_col = QVBoxLayout()
        name_row = QHBoxLayout()
        name = QLabel(f"<b>{item['name']}</b>")
        name.setTextFormat(Qt.TextFormat.RichText)
        cat = QLabel(item["category"])
        cat.setProperty("class", "muted")
        name_row.addWidget(name)
        name_row.addWidget(cat)
        name_row.addStretch(1)
        text_col.addLayout(name_row)
        desc = QLabel(item["description"])
        desc.setProperty("class", "muted")
        desc.setWordWrap(True)
        text_col.addWidget(desc)
        layout.addLayout(text_col, 1)

        price = QLabel(fmt_currency(item["price"]))
        price.setStyleSheet("color:#c9a84c; font-weight:600;")
        layout.addWidget(price)

        minus = QPushButton("−")
        minus.setObjectName("qtyButton")
        minus.clicked.connect(lambda _checked, i=item["id"]: self._adjust(i, -1))
        layout.addWidget(minus)

        qty_label = QLabel(str(self._orders.get(item["id"], 0)))
        qty_label.setFixedWidth(24)
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_labels[item["id"]] = qty_label
        layout.addWidget(qty_label)

        plus = QPushButton("+")
        plus.setObjectName("qtyButton")
        plus.clicked.connect(lambda _checked, i=item["id"]: self._adjust(i, 1))
        layout.addWidget(plus)

        return row_frame

    def _adjust(self, item_id: int, delta: int) -> None:
        new_qty = max(0, self._orders.get(item_id, 0) + delta)
        if new_qty == 0:
            self._orders.pop(item_id, None)
        else:
            self._orders[item_id] = new_qty
        if item_id in self._qty_labels:
            self._qty_labels[item_id].setText(str(new_qty))
        self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        while self._order_lines_host.count():
            item = self._order_lines_host.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self._orders:
            self._empty_label.show()
            self._total_label.setText("Dining Total: ₱0")
            return

        self._empty_label.hide()
        total = 0
        for item_id, qty in self._orders.items():
            item = find_dining_item(item_id)
            total += item["price"] * qty
            line = QLabel(f"{item['name']} ×{qty} — {fmt_currency(item['price'] * qty)}")
            line.setProperty("class", "muted")
            self._order_lines_host.addWidget(line)
        self._total_label.setText(f"Dining Total: {fmt_currency(total)}")

    def _dining_list(self) -> list:
        return [dict(item=find_dining_item(iid), qty=qty) for iid, qty in self._orders.items()]

    def _continue(self) -> None:
        booking = {**self._booking, "dining": self._dining_list()}
        self.go("services", booking=booking)

    def _skip(self) -> None:
        booking = {**self._booking, "dining": []}
        self.go("services", booking=booking)

    def _back(self) -> None:
        self.go("booking", room=self._booking["room"])
