"""
views/__init__.py
Package exports — lets main.py do:

    from views import (
        HomeView, RoomsView, RoomDetailView, BookingView,
        DiningView, ServicesView, PaymentView, ReceiptView,
    )
"""

from .home_view import HomeView
from .rooms_view import RoomsView
from .room_detail_view import RoomDetailView
from .booking_view import BookingView
from .dining_view import DiningView
from .services_view import ServicesView
from .payment_view import PaymentView
from .receipt_view import ReceiptView

__all__ = [
    "HomeView", "RoomsView", "RoomDetailView", "BookingView",
    "DiningView", "ServicesView", "PaymentView", "ReceiptView",
]
