# easily turn number into pesos lmao like (67 -> ₱67.00) with TWO decimal places, im so cool
def fmt_currency(amount):
    return f"₱{amount:,.2f}"
