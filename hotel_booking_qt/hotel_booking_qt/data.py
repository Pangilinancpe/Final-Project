"""
data.py
Mock datasets: rooms, dining menu items, and add-on services, plus small
lookup helpers. Pure data — no PyQt import here, so it can be unit-tested
or reused without a QApplication instance running.
"""

ROOMS = [
    dict(id=1, tier="Premium", name="Premier Grand Suite", pricePerDay=12500, pricePerHour=1800,
         size="85 m²", maxGuests=4,
         image="https://images.unsplash.com/photo-1776763018972-588e27bf6511?w=800&h=500&fit=crop&auto=format",
         amenities=["King Bed", "Ocean View", "Jacuzzi", "Minibar", "Private Balcony", "Butler Service", "Smart TV", "Free WiFi"],
         details="Our most luxurious offering. A sprawling suite with floor-to-ceiling windows, a marble bathroom with jacuzzi, and a private balcony overlooking the bay."),

    dict(id=2, tier="Premium", name="Executive Pool Suite", pricePerDay=9800, pricePerHour=1400,
         size="70 m²", maxGuests=3,
         image="https://images.unsp lash.com/photo-1758448755969-8791367cf5c5?w=800&h=500&fit=crop&auto=format",
         amenities=["King Bed", "Pool Access", "Spa Bath", "Minibar", "Lounge Area", "Concierge", "Smart TV"],
         details="Direct access to the infinity pool from your suite. Perfect for those who want the ultimate indulgence with panoramic city views."),

    dict(id=3, tier="Deluxe", name="Deluxe Family Room", pricePerDay=5500, pricePerHour=800,
         size="55 m²", maxGuests=5,
         image="https://images.unsplash.com/photo-1788217023349-ad7763845844?w=800&h=500&fit=crop&auto=format",
         amenities=["1 King + 2 Twin Beds", "Garden View", "Rain Shower", "Minibar", "Dining Table", "Smart TV", "Free WiFi"],
         details="Thoughtfully designed for families. Features separate sleeping areas, a dedicated dining space, and child-friendly amenities."),

    dict(id=4, tier="Deluxe", name="Deluxe Superior Room", pricePerDay=4200, pricePerHour=600,
         size="42 m²", maxGuests=2,
         image="https://images.unsplash.com/photo-1638277000768-005d326db4b2?w=800&h=500&fit=crop&auto=format",
         amenities=["Queen Bed", "City View", "Walk-in Shower", "Minibar", "Work Desk", "Smart TV"],
         details="Elegant and versatile. The Deluxe Superior provides a refined base for both business and leisure travelers with modern comforts."),

    dict(id=5, tier="Economy", name="Economy Standard Room", pricePerDay=1800, pricePerHour=280,
         size="28 m²", maxGuests=2,
         image="https://images.unsplash.com/photo-1677129667171-92abd8740fa3?w=800&h=500&fit=crop&auto=format",
         amenities=["Double Bed", "Partial View", "Shower", "Cable TV", "Free WiFi"],
         details="Clean, comfortable, and great value. Everything you need for a pleasant stay without the extras."),

    dict(id=6, tier="Economy", name="Economy Twin Room", pricePerDay=1600, pricePerHour=250,
         size="26 m²", maxGuests=2,
         image="https://images.unsplash.com/photo-1581115685033-ccf1aa701722?w=800&h=500&fit=crop&auto=format",
         amenities=["2 Single Beds", "Standard View", "Shower", "Cable TV", "Free WiFi", "Workspace"],
         details="Ideal for two guests traveling together. Two separate beds, practical layout, and all the essential amenities."),
]

DINING = [
    dict(id=1, name="Eggs Benedict", category="Breakfast", price=380, description="Poached eggs, Canadian bacon, hollandaise on toasted muffin"),
    dict(id=2, name="Filipino Breakfast Set", category="Breakfast", price=320, description="Sinangag, sunny-side egg, choice of tocino or longganisa"),
    dict(id=3, name="Club Sandwich", category="All-day", price=420, description="Triple-decker with chicken, bacon, lettuce, tomato, served with fries"),
    dict(id=4, name="Beef Kare-Kare", category="Filipino", price=680, description="Slow-braised beef in rich peanut sauce with vegetables and bagoong"),
    dict(id=5, name="Grilled Salmon", category="International", price=850, description="Norwegian salmon, lemon-dill butter, steamed vegetables, rice"),
    dict(id=6, name="Chicken Adobo", category="Filipino", price=480, description="Classic Filipino adobo with garlic rice and pickled vegetables"),
    dict(id=7, name="Margherita Pizza", category="All-day", price=550, description="San Marzano tomatoes, fresh mozzarella, basil, olive oil"),
    dict(id=8, name="Mango Float", category="Dessert", price=280, description="Layers of cream, graham crackers, and fresh Carabao mangoes"),
]

SERVICES = [
    dict(id=1, name="Airport Transfer (one-way)", price=850, description="Air-conditioned van, meet & greet service"),
    dict(id=2, name="Laundry Service (per kg)", price=150, description="Wash, dry, and fold. Same-day delivery available."),
    dict(id=3, name="In-Room Spa Massage (60 min)", price=1800, description="Choose from Swedish, Shiatsu, or Hilot"),
    dict(id=4, name="Extra Bed", price=600, description="Rollaway bed with linens and pillow"),
    dict(id=5, name="Late Checkout (until 3PM)", price=1000, description="Standard checkout is 12PM noon"),
    dict(id=6, name="Celebration Package", price=2500, description="Cake, balloons, rose petals, welcome card"),
]


def find_room(room_id: int) -> dict:
    return next(r for r in ROOMS if r["id"] == room_id)


def find_dining_item(item_id: int) -> dict:
    return next(d for d in DINING if d["id"] == item_id)


def find_service_item(item_id: int) -> dict:
    return next(s for s in SERVICES if s["id"] == item_id)
