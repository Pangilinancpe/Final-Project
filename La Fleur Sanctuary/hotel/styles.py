"""styles.py — the global Qt stylesheet."""

from config import COLORS as C

QSS_STYLE = f"""
QWidget {{ background-color: {C['bg']}; color: {C['cream']}; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; }}
QLabel, QFrame#stepper {{ background: transparent; }}
QScrollArea {{ border: none; background-color: {C['bg']}; }}

QLabel[class="muted"] {{ color: {C['muted']}; font-size: 11px; }}
QLabel#sectionKicker, QLabel#heroKicker {{ color: {C['gold']}; font-size: 11px; font-weight: 600; }}
QLabel#sectionTitle {{ font-size: 20px; font-weight: 600; }}
QLabel#heroTitle {{ font-size: 32px; font-weight: 600; }}
QLabel#heroSub {{ color: {C['tan']}; }}
QLabel#chipLabel {{ color: {C['tan']}; font-size: 11px; border: 1px solid {C['border']}; border-radius: 11px; padding: 4px 12px; }}
QLabel#errorText {{ color: {C['red']}; font-size: 11px; }}

QFrame#navbar {{ border-bottom: 1px solid {C['border']}; }}
QFrame#card {{ background-color: {C['panel']}; border: 1px solid {C['border']}; border-radius: 10px; }}
QFrame#divider {{ background-color: {C['border']}; border: none; }}
QFrame#overlay {{ background-color: rgba(13, 17, 23, 170); }}
QFrame#errorBox {{ background-color: rgba(220, 38, 38, 30); border: 1px solid rgba(239, 68, 68, 76); border-radius: 6px; }}

QPushButton#brandButton {{ background: transparent; border: none; font-size: 15px; font-weight: 600; text-align: left; padding: 4px; }}
QPushButton#brandButton:hover, QPushButton#linkButton:hover {{ color: {C['gold']}; }}
QPushButton#linkButton {{ background: transparent; border: none; color: {C['muted']}; padding: 4px; }}

QPushButton#primaryButton {{ background-color: {C['gold']}; color: {C['bg']}; border: none; border-radius: 6px; padding: 10px 18px; font-weight: 600; }}
QPushButton#primaryButton:hover {{ background-color: {C['gold_hover']}; }}
QPushButton#primaryButton:disabled {{ background-color: {C['border']}; color: {C['muted']}; }}

QPushButton#ghostButton {{ background: transparent; color: {C['muted']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 8px 14px; }}
QPushButton#ghostButton:hover {{ color: {C['cream']}; border: 1px solid {C['gold']}; }}

QPushButton#tabButton {{ background: transparent; color: {C['muted']}; border: 1px solid {C['border']}; border-radius: 15px; padding: 6px 18px; }}
QPushButton#tabButton:hover {{ color: {C['cream']}; border: 1px solid {C['gold']}; }}
QPushButton#tabButton:checked {{ background-color: {C['gold']}; color: {C['bg']}; border: 1px solid {C['gold']}; font-weight: 600; }}

QPushButton#qtyButton {{ background-color: {C['panel2']}; border: 1px solid {C['border']}; border-radius: 4px; font-weight: 700; min-width: 26px; max-width: 26px; min-height: 26px; max-height: 26px; }}
QPushButton#qtyButton:hover {{ border: 1px solid {C['gold']}; }}

QPushButton#paymentOption {{ background-color: {C['panel']}; border: 1px solid {C['border']}; border-radius: 8px; padding: 14px; text-align: left; font-weight: 500; }}
QPushButton#paymentOption:hover {{ border: 1px solid {C['gold']}; }}
QPushButton#paymentOption:checked {{ border: 1px solid {C['gold']}; background-color: rgba(201, 168, 76, 40); color: {C['gold']}; }}

QLineEdit, QSpinBox, QComboBox {{ background-color: {C['panel2']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 6px 10px; }}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border: 1px solid {C['gold']}; }}
QComboBox QAbstractItemView {{ background-color: {C['panel2']}; selection-background-color: {C['gold']}; selection-color: {C['bg']}; }}

QScrollBar:vertical {{ background: {C['bg']}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {C['border']}; border-radius: 5px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: {C['gold']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
"""
