# This the freaking shared Qt stylesheet. Apply once to QApplication in main.py

from config import COLORS

QSS_STYLE = f"""
QWidget {{
    background: {COLORS['background']};
    color: {COLORS['text']};
    font: 14px 'Segoe UI';
}}
QFrame#serviceCard {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 8px;
}}
QFrame#serviceCard QLabel {{ background: transparent; }}
QLabel#pageTitle {{ font-size: 26px; font-weight: bold; }}
QLabel#stepLabel, QLabel#servicePrice {{ color: {COLORS['gold_text']}; }}
QLabel#serviceName, QLabel#serviceSummary {{
    font-size: 17px;
    font-weight: bold;
}}
QPushButton {{
    background: {COLORS['button']};
    border: 1px solid {COLORS['input_border']};
    padding: 9px;
    border-radius: 5px;
}}
QPushButton:hover {{ background: {COLORS['button_hover']}; }}
QPushButton#primaryButton {{
    background: {COLORS['primary_button']};
    color: {COLORS['primary_text']};
    font-weight: bold;
}}
QSpinBox {{
    background: {COLORS['background']};
    padding: 6px;
    border: 1px solid {COLORS['input_border']};
}}
"""