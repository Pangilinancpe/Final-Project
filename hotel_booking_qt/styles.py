
from config import COLORS

QSS_STYLE = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['cream']};
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {COLORS['bg']};
}}

QScrollArea {{
    border: none;
    background-color: {COLORS['bg']};
}}

QLabel[class="muted"] {{
    color: {COLORS['muted']};
    font-size: 11px;
}}

QLabel#sectionKicker {{
    color: {COLORS['gold']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
}}

QLabel#sectionTitle {{
    font-size: 20px;
    font-weight: 600;
    color: {COLORS['cream']};
}}

QLabel#heroKicker {{
    color: {COLORS['gold']};
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: 600;
}}

QLabel#heroTitle {{
    font-size: 32px;
    font-weight: 600;
    color: {COLORS['cream']};
}}

QLabel#heroSub {{
    color: {COLORS['tan']};
    font-size: 13px;
}}

QFrame#navbar {{
    background-color: {COLORS['bg']};
    border-bottom: 1px solid {COLORS['border']};
}}

QFrame#card {{
    background-color: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
}}

QPushButton {{
    font-family: inherit;
}}

QPushButton#brandButton {{
    background-color: transparent;
    border: none;
    font-size: 15px;
    font-weight: 600;
    color: {COLORS['cream']};
    text-align: left;
    padding: 4px;
}}
QPushButton#brandButton:hover {{
    color: {COLORS['gold']};
}}

QPushButton#primaryButton {{
    background-color: {COLORS['gold']};
    color: {COLORS['bg']};
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{
    background-color: {COLORS['gold_hover']};
}}
QPushButton#primaryButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['muted']};
}}

QPushButton#ghostButton {{
    background-color: transparent;
    color: {COLORS['muted']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 14px;
}}
QPushButton#ghostButton:hover {{
    color: {COLORS['cream']};
    border: 1px solid {COLORS['gold']};
}}

QPushButton#linkButton {{
    background: transparent;
    border: none;
    color: {COLORS['muted']};
    padding: 4px;
}}
QPushButton#linkButton:hover {{
    color: {COLORS['gold']};
}}

QPushButton#qtyButton {{
    background-color: {COLORS['panel2']};
    color: {COLORS['cream']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    font-weight: 700;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}}
QPushButton#qtyButton:hover {{
    border: 1px solid {COLORS['gold']};
}}

QPushButton#paymentOption {{
    background-color: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 14px;
    text-align: left;
    font-weight: 500;
}}
QPushButton#paymentOption:checked {{
    border: 1px solid {COLORS['gold']};
    background-color: rgba(201, 168, 76, 40);
    color: {COLORS['gold']};
}}
QPushButton#paymentOption:hover {{
    border: 1px solid {COLORS['gold']};
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: {COLORS['panel2']};
    color: {COLORS['cream']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLORS['gold']};
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['panel2']};
    color: {COLORS['cream']};
    selection-background-color: {COLORS['gold']};
    selection-color: {COLORS['bg']};
}}

QRadioButton {{
    color: {COLORS['cream']};
    spacing: 6px;
}}

QLabel#chipLabel {{
    color: {COLORS['tan']};
    font-size: 11px;
    border: 1px solid {COLORS['border']};
    border-radius: 11px;
    padding: 4px 12px;
}}

QFrame#errorBox {{
    background-color: rgba(220, 38, 38, 30);
    border: 1px solid rgba(239, 68, 68, 76);
    border-radius: 6px;
}}
QLabel#errorText {{
    color: {COLORS['red']};
    font-size: 11px;
}}

QScrollBar:vertical {{
    background: {COLORS['bg']};
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['gold']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
