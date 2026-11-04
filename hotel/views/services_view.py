"""views/services_view.py — Step 3 of 4: optional add-on services (grid of qty cards)."""

from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QVBoxLayout

from config import COLORS
from data import SERVICES, find_service_item
from utils import CoverImage, Stepper, button, fmt_currency, label, load_service_image
from views.base_view import BaseView


class ServicesView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._booking, self._selected, self._steppers, self._images = None, {}, {}, {}
        outer = self.make_page(back=self._back, cancel=True)
        outer.addWidget(label("STEP 3 OF 4", "sectionKicker"))
        outer.addWidget(label("Additional Services", "sectionTitle"))
        outer.addWidget(label("Enhance your stay with our curated add-ons.", muted=True))

        grid = QGridLayout()
        grid.setSpacing(16)
        for i, svc in enumerate(SERVICES):
            grid.addWidget(self._card(svc), i // 2, i % 2)
        grid.setRowStretch(len(SERVICES), 1)
        self.add_scroll(outer, grid)

        row = QHBoxLayout()
        row.addWidget(button("Skip", "ghostButton", self._skip))
        row.addWidget(button("Continue to Payment →", "primaryButton", self._continue), 1)
        outer.addLayout(row)

    def on_enter(self, payload: dict) -> None:
        if payload.get("booking") is None:
            return
        self._booking = payload["booking"]
        self._selected = {d["item"]["id"]: d["qty"] for d in self._booking.get("extraServices", [])}  # restores on Back
        for sid, stepper in self._steppers.items():
            stepper.set(self._selected.get(sid, 0), emit=False)

    def on_show(self) -> None:
        """Load the pictures the first time this screen appears (may download them once from GitHub)."""
        for svc in SERVICES:
            if self._images[svc["id"]]._pm is None:
                self._images[svc["id"]].set_pixmap(load_service_image(svc["image"]))

    def _card(self, svc: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        self._images[svc["id"]] = CoverImage(130)
        lay.addWidget(self._images[svc["id"]])
        lay.addWidget(label(f"<b>{svc['name']}</b>"))
        lay.addWidget(label(svc["description"], muted=True, wrap=True))
        bottom = QHBoxLayout()
        bottom.addWidget(label(fmt_currency(svc["price"]), style=f"color:{COLORS['gold']}; font-weight:600;"))
        bottom.addStretch(1)
        stepper = Stepper()
        stepper.changed.connect(lambda qty, sid=svc["id"]: self._set_qty(sid, qty))
        self._steppers[svc["id"]] = stepper
        bottom.addWidget(stepper)
        lay.addLayout(bottom)
        return card

    def _set_qty(self, sid: int, qty: int) -> None:
        if qty:
            self._selected[sid] = qty
        else:
            self._selected.pop(sid, None)

    def _next(self, with_services: bool) -> None:
        extras = [dict(item=find_service_item(i), qty=q) for i, q in self._selected.items()] if with_services else []
        self.go("payment", booking={**self._booking, "extraServices": extras})

    def _continue(self) -> None:
        self._next(True)

    def _skip(self) -> None:
        self._next(False)

    def _back(self) -> None:
        self.go("dining", booking=self._booking)
