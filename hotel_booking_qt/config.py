"""
config.py
App-wide constants: color tokens, tier colors, payment methods, and shared
numeric settings. Centralized here so styles.py, data.py and the views never
hardcode the same color/number in more than one place.
"""

APP_TITLE = "Maison Élara"
APP_SUBTITLE = "Hotel Booking System"
WINDOW_MIN_SIZE = (1200, 800)

COLORS = {
    "bg": "#0d1117",
    "panel": "#161c27",
    "panel2": "#1a2030",
    "border": "#2a3347",
    "gold": "#c9a84c",
    "gold_hover": "#d4b65e",
    "cream": "#f0ead6",
    "tan": "#b8a98e",
    "muted": "#7a8499",
    "green": "#4ade80",
    "red": "#f87171",
}

TIER_COLORS = {
    "Premium": "#c9a84c",
    "Deluxe": "#7c9fc9",
    "Economy": "#7ab87a",
}

# (key, label, emoji icon) — order matters, it's the display order in PaymentView.
PAYMENT_METHODS = [
    ("cash", "Cash Payment", "💵"),
    ("ewallet", "E-Wallet (GCash / Maya)", "📱"),
    ("ebanking", "Online Banking", "🏦"),
    ("card", "Credit / Debit Card", "💳"),
]
PAYMENT_LABELS = {key: label for key, label, _icon in PAYMENT_METHODS}

FAMILY_DISCOUNT_RATE = 0.10
MIN_GUESTS = 2
MAX_GUESTS_SPIN = 10

HOTEL_NAME = "Maison Élara Hotel"
HOTEL_LOCATION = "Manila, Philippines"
HOTEL_HOTLINE = "(02) 8888-1234"
