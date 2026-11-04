"""widgets/name_row.py — one person's name split into First name · M.I. · Last name · Suffix."""

from PyQt6.QtWidgets import QComboBox, QGridLayout, QLineEdit, QWidget

from config import NAME_SUFFIXES
from utils import label


def _clean(text: str) -> str:
    return " ".join(text.split())


def _only_letters(text: str) -> bool:
    return all(ch.isalpha() or ch in " .'-" for ch in text)


class NameRow(QWidget):
    """Four boxes in one row. text() gives 'Juan D. Cruz Jr.'; parts()/set_parts() keep the boxes for going back."""

    def __init__(self, who: str = "Guest"):
        super().__init__()
        self._who = who
        self.first, self.middle, self.last = QLineEdit(), QLineEdit(), QLineEdit()
        self.suffix = QComboBox()
        self.first.setPlaceholderText("e.g. Juan")
        self.middle.setPlaceholderText("D")
        self.middle.setMaxLength(2)           # one letter, plus an optional dot
        self.last.setPlaceholderText("e.g. Cruz")
        self.suffix.addItems(NAME_SUFFIXES)
        self.suffix.setItemText(0, "None")
        self.middle.setFixedWidth(64)
        self.suffix.setFixedWidth(96)

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(2)
        for col, (caption, box) in enumerate((("First name", self.first), ("M.I.", self.middle),
                                              ("Last name", self.last), ("Suffix (Sr., Jr.)", self.suffix))):
            grid.addWidget(label(caption, muted=True), 0, col)
            grid.addWidget(box, 1, col)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(2, 3)

    def parts(self) -> dict:
        suffix = self.suffix.currentText()
        return dict(first=_clean(self.first.text()), middle=_clean(self.middle.text()).rstrip(".").upper(),
                    last=_clean(self.last.text()), suffix="" if suffix == "None" else suffix)

    def set_parts(self, parts: dict) -> None:
        self.first.setText(parts.get("first", ""))
        self.middle.setText(parts.get("middle", ""))
        self.last.setText(parts.get("last", ""))
        index = self.suffix.findText(parts.get("suffix", "") or "None")
        self.suffix.setCurrentIndex(max(0, index))

    def text(self) -> str:
        p = self.parts()
        pieces = [p["first"], p["middle"] + "." if p["middle"] else "", p["last"], p["suffix"]]
        return " ".join(x for x in pieces if x)

    def error(self):
        """None when the name is fine, otherwise a sentence for the red message box."""
        p = self.parts()
        if not p["first"]:
            return f"Enter the first name of {self._who}."
        if not p["last"]:
            return f"Enter the last name of {self._who}."
        if not all(_only_letters(v) for v in (p["first"], p["last"], p["middle"])):
            return f"The name of {self._who} should contain letters only."
        if len(p["middle"]) > 1:
            return f"The middle initial of {self._who} must be a single letter."
        return None
