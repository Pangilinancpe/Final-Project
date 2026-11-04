from copy import deepcopy
from pathlib import Path

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget

from .base_view import BaseView
from config import COLORS, SERVICE_IMAGE_OPACITY, SERVICE_FADE_STOPS
from data import SERVICES
from utils import fmt_currency


class ServiceCard(QFrame):
    # This part is for the image behind the panels with an implementation of a fade
    def __init__(self, service_id):
        super().__init__()
        self.setObjectName("serviceCard")
        self.setMinimumHeight(220)
        # Resolve from this file so launching from another folder still works.
        folder = Path(__file__).resolve().parent.parent / "assets" / "services"
        self.background = QPixmap()
        for extension in ("png", "jpg", "jpeg", "webp"):
            path = folder / f"{service_id}.{extension}"
            if path.is_file():
                self.background = QPixmap(str(path))
                if not self.background.isNull():
                    break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        clip = QPainterPath()
        clip.addRoundedRect(rect, 9, 9)
        painter.setClipPath(clip)
        painter.fillRect(rect, QColor(COLORS["card"]))

        if not self.background.isNull():
            # Cover the card without stretching; excess edges are cropped.
            scaled = self.background.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setOpacity(SERVICE_IMAGE_OPACITY)
            painter.drawPixmap(
                (self.width() - scaled.width()) // 2,
                (self.height() - scaled.height()) // 2, scaled,
            )
            painter.setOpacity(1.0)
            fade = QLinearGradient(0, 0, self.width(), 0)
            for position, alpha in SERVICE_FADE_STOPS:
                color = QColor(COLORS["card"])
                color.setAlpha(alpha)
                fade.setColorAt(position, color)
            painter.fillRect(rect, fade)

        painter.setPen(QPen(QColor("#364154"), 1))
        painter.drawRoundedRect(rect, 9, 9)


class ServicesView(BaseView):
    # Main services_view page (main still owns navigation rights, etc. etc.)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.booking = {}
        self.quantity_inputs = {}
        self.line_labels = {}
        self.services = SERVICES
        self._build_ui()
        self._update_summary()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        step = QLabel("STEP 3 OF 4  •  OPTIONAL EXTRAS")
        step.setObjectName("stepLabel")
        layout.addWidget(step)
        title = QLabel("Make your stay more comfortable")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        description = QLabel(
            "Choose your add-on services below. You can also continue without extras."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Scroll for cards but not allowing the navigation buttons to go away
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        cards = QGridLayout(content)
        cards.setContentsMargins(0, 0, 8, 0)
        cards.setSpacing(12)
        for index, service in enumerate(self.services):
            card = self._make_card(service)
            cards.addWidget(card, index // 2, index % 2)
        cards.setColumnStretch(0, 1)
        cards.setColumnStretch(1, 1)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("serviceSummary")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        note = QLabel("Service subtotal only. Your full bill is shown at payment.")
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QHBoxLayout()
        self.back_button = QPushButton("Back to Dining")
        self.skip_button = QPushButton("Skip Services")
        self.continue_button = QPushButton("Continue to Payment")
        self.continue_button.setObjectName("primaryButton")
        self.back_button.clicked.connect(self._back)
        self.skip_button.clicked.connect(self._skip)
        self.continue_button.clicked.connect(self._continue)
        buttons.addWidget(self.back_button)
        buttons.addStretch()
        buttons.addWidget(self.skip_button)
        buttons.addWidget(self.continue_button)
        layout.addLayout(buttons)

    def _make_card(self, service):
        card = ServiceCard(service["id"])
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        name = QLabel(service["name"])
        name.setObjectName("serviceName")
        name.setWordWrap(True)
        layout.addWidget(name)
        description = QLabel(service["description"])
        description.setWordWrap(True)
        description.setMaximumWidth(460)
        layout.addWidget(description)
        price = QLabel(
            f'{fmt_currency(service["price"])} / {service["unit"]}'
        )
        price.setObjectName("servicePrice")
        layout.addWidget(price)
        layout.addStretch()

        controls = QHBoxLayout()
        minus = QPushButton("−")
        plus = QPushButton("+")
        minus.setFixedWidth(36)
        plus.setFixedWidth(36)
        quantity = QSpinBox()
        quantity.setRange(0, service["max_quantity"])
        quantity.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        quantity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quantity.setFixedWidth(64)
        quantity.setAccessibleName(f'Quantity for {service["name"]}')
        minus.setAccessibleName(f'Remove one {service["name"]}')
        plus.setAccessibleName(f'Add one {service["name"]}')
        minus.clicked.connect(
            lambda checked=False: self._change_quantity(quantity, -1)
        )
        plus.clicked.connect(
            lambda checked=False: self._change_quantity(quantity, 1)
        )
        quantity.valueChanged.connect(self._update_summary)
        self.quantity_inputs[service["id"]] = quantity
        controls.addWidget(QLabel("Quantity"))
        controls.addStretch()
        controls.addWidget(minus)
        controls.addWidget(quantity)
        controls.addWidget(plus)
        layout.addLayout(controls)
        line_label = QLabel()
        self.line_labels[service["id"]] = line_label
        layout.addWidget(line_label)
        return card

    def _change_quantity(self, quantity, step):
        # Text gets selected after increasing quantity for some reason (fixed via deselecting)
        quantity.stepBy(step)
        quantity.lineEdit().deselect()

    def on_enter(self, data=None):
        # Load full booking, no services selection means nothing was picked
        self.booking = deepcopy(data) if data is not None else {}
        saved = self.booking.get("services", {})
        for service in self.services:
            service_id = service["id"]
            quantity = saved.get(service_id, 0)

            if type(quantity) is not int or quantity < 0:
                quantity = 0
            widget = self.quantity_inputs[service_id]
            widget.blockSignals(True)
            widget.setValue(quantity)
            widget.blockSignals(False)
        self._update_summary()

    def get_selected_services(self):
        # Return the only selected IDs and quantities, e.g. {'laundry': 2, etc.}
        selected = {}
        for service_id, widget in self.quantity_inputs.items():
            if widget.value() > 0:
                selected[service_id] = widget.value()
        return selected

    def get_services_total(self):
        total = 0
        for service in self.services:
            quantity = self.quantity_inputs[service["id"]].value()
            total += service["price"] * quantity
        return total

    def _update_summary(self):
        count = 0
        for service in self.services:
            quantity = self.quantity_inputs[service["id"]].value()
            count += quantity
            line_total = service["price"] * quantity
            self.line_labels[service["id"]].setText(
                f"Line total: {fmt_currency(line_total)}"
            )
        self.summary_label.setText(
            f"Selected units: {count}    |    "
            f"Services subtotal: {fmt_currency(self.get_services_total())}"
        )

    def _send_booking(self, destination):
        # save room, guest, dining, and any other parts that other members own (for easier modularity)
        data = deepcopy(self.booking)
        data["services"] = self.get_selected_services()
        self.booking = deepcopy(data)
        self.go(destination, data)

    def _back(self):
        self._send_booking("dining")

    def _continue(self):
        self._send_booking("payment")

    def _skip(self):
        # removes earlier selections if 'skip' is pressed
        for widget in self.quantity_inputs.values():
            widget.blockSignals(True)
            widget.setValue(0)
            widget.blockSignals(False)
        self._update_summary()
