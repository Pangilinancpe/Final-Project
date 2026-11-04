"""config.py — app-wide constants (colors, tiers, payment methods, numeric settings)."""

APP_TITLE = "La Fleur Sanctuary"
APP_SUBTITLE = "Hotel Booking System"
WINDOW_MIN_SIZE = (1200, 800)

COLORS = {
    "bg": "#0d1117", "panel": "#161c27", "panel2": "#1a2030", "border": "#2a3347",
    "gold": "#c9a84c", "gold_hover": "#d4b65e", "cream": "#f0ead6", "tan": "#b8a98e",
    "muted": "#7a8499", "green": "#4ade80", "red": "#f87171",
}

TIER_COLORS = {"Executive": "#d9774a", "Suite": "#8fb04a", "Presidential": "#9b7de0"}

# (key, label, icon) — display order in PaymentView
PAYMENT_METHODS = [
    ("cash", "Cash Payment", "💵"),
    ("ewallet", "E-Wallet (GCash / Maya)", "📱"),
    ("ebanking", "Online Banking", "🏦"),
    ("card", "Credit / Debit Card", "💳"),
]
PAYMENT_LABELS = {key: label for key, label, _icon in PAYMENT_METHODS}

# Rows shown on the checkout screen, in order: (row id, label, method key saved in the booking, e-wallet name or None)
PAYMENT_OPTIONS = [
    ("gcash", "GCash", "ewallet", "GCash"),
    ("maya", "Maya", "ewallet", "Maya"),
    ("card", "Credit / Debit Card", "card", None),
    ("ebanking", "Online Banking", "ebanking", None),
    ("cash", "Cash at Front Desk", "cash", None),
]

NAME_SUFFIXES = ("", "Sr.", "Jr.", "II", "III", "IV", "V")

FAMILY_DISCOUNT_RATE = 0.10
MIN_GUESTS = 1
MAX_GUESTS = 2  # guests allowed per booking (a room's own capacity can be lower)
EWALLET_PROVIDERS = ("GCash", "Maya")

HOTEL_NAME = "La Fleur Sanctuary"
HOTEL_LOCATION = "Manila, Philippines"
HOTEL_HOTLINE = "(02) 8888-1234"

# Service pictures: looked up in ./assets/services first, otherwise downloaded once from the repo and saved there.
SERVICE_IMAGES_URL = "https://raw.githubusercontent.com/Pangilinancpe/Final-Project/main/assets/services/"

HERO_IMAGE_URL = "https://images.unsplash.com/photo-1677129667171-92abd8740fa3?w=1400&h=600&fit=crop&auto=format"
