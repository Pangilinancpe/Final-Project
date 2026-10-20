# config.py
# Settings and constants used all over the app.
# If you want to change a color, price rule, or hotel detail, do it here.

# App window
APP_TITLE = "-------"
APP_SUBTITLE = "------"
WINDOW_MIN_SIZE = (1200, 800)

# Hotel info
HOTEL_NAME = "----"
HOTEL_LOCATION = "Manila, Philippines"
HOTEL_HOTLINE = "----"

# Colors for the dark and gold theme, written as rgb(red, green, blue)
COLORS = {
    "bg": "rgb(13, 17, 23)",            # main background
    "panel": "rgb(22, 28, 39)",         # cards
    "panel2": "rgb(26, 32, 48)",        # inputs and buttons
    "border": "rgb(42, 51, 71)",
    "gold": "rgb(201, 168, 76)",
    "gold_hover": "rgb(212, 182, 94)",
    "cream": "rgb(240, 234, 214)",      # main text
    "tan": "rgb(184, 169, 142)",
    "muted": "rgb(122, 132, 153)",      # small gray text
    "green": "rgb(74, 222, 128)",       # discounts
    "red": "rgb(248, 113, 113)",        # errors
}

# One color for each room type
TIER_COLORS = {
    "Premium": "rgb(201, 168, 76)",
    "Deluxe": "rgb(124, 159, 201)",
    "Economy": "rgb(122, 184, 122)",
}


def with_alpha(color, alpha):
    # "rgb(201, 168, 76)" becomes "rgba(201, 168, 76, 26)"
    # alpha: 0 is invisible, 255 is solid
    return color.replace("rgb", "rgba").replace(")", ", " + str(alpha) + ")")


# Payment options: (key, name shown on the button, icon)
# They show up on the payment page in this order.
PAYMENT_METHODS = [
    ("cash", "Cash Payment", "💵"),
    ("ewallet", "E-Wallet (GCash / Maya)", "📱"),
    ("ebanking", "Online Banking", "🏦"),
    ("card", "Credit / Debit Card", "💳"),
]

# Quick lookup, for example "cash" -> "Cash Payment" (used on the receipt)
PAYMENT_LABELS = {key: label for key, label, icon in PAYMENT_METHODS}

# Booking rules
FAMILY_DISCOUNT_RATE = 0.10   # 10% off when there is a senior or a child
MIN_GUESTS = 2                # a booking needs at least 2 guests
MAX_GUESTS_SPIN = 10          # highest number you can pick in the guest boxes