"""data.py — mock data (rooms, dining, services). Pure data, no PyQt."""

from config import MAX_GUESTS

# (tier key, title, blurb) — shared by the home screen and the rooms screen
TIERS = [
    ("Executive", "Executive Rooms", "Comfortable, well-appointed rooms for business and leisure stays."),
    ("Suite", "Suite Rooms", "Spacious suites with separate living areas and a more special touch."),
    ("Presidential", "Presidential Rooms", "Our most exclusive rooms, with VIP amenities and private services."),
]

# tier -> [(name, price per day, size m², max guests, amenities)]
_CATALOG = {
    "Executive": [
        ("Luxe", 4200, 32, 2, ["King bed with cotton linens", '55" Smart TV', "Free high-speed Wi-Fi", "Rain shower", "Mini fridge"]),
        ("Elysian", 4500, 34, 2, ["Queen bed", "Work desk with ergonomic chair", "Coffee machine with capsules", "Free high-speed Wi-Fi", "City view window"]),
        ("Velvet", 4800, 36, 2, ["Two twin beds", "Soaking bathtub", "Complimentary breakfast for 2", "Smart TV with streaming apps", "Free high-speed Wi-Fi"]),
        ("Emerald", 4600, 35, 2, ["King bed", "Garden view", "Tea and herbal set", "In-room yoga mat", "Free high-speed Wi-Fi"]),
        ("Silk", 5000, 38, 2, ["Queen bed with silk-blend linens", "Bluetooth speaker", "Stocked minibar", "Bathrobe and slippers", "Free high-speed Wi-Fi"]),
        ("Elite", 5400, 40, 2, ["King bed", "Executive lounge access", "Work desk and printer access", "Ironing set", "Free high-speed Wi-Fi"]),
        ("Grand", 5800, 48, 4, ["Two queen beds (family-sized)", "Sofa and seating area", "Smart TV with streaming apps", "Complimentary breakfast for 4", "Free high-speed Wi-Fi"]),
    ],
    "Suite": [
        ("Prestige", 9800, 65, 3, ["King bed with separate living room", "Soaking bathtub and rain shower", "Premium coffee and tea station", "Complimentary breakfast for 2", "Pool and fitness access", "Free high-speed Wi-Fi"]),
        ("Imperial", 11500, 75, 3, ["Panoramic city view", "In-room jacuzzi", "Private lounge and dining nook", "Evening wine and cheese service", "Late check-out until 3 PM", "Smart-home controls for lights and curtains"]),
        ("Opulent", 13200, 90, 4, ["Two bedrooms with a full dining area", "Spa bath with aromatherapy", "Butler service on request", "Free airport transfer", "Premium stocked minibar", "Complimentary breakfast for 4"]),
    ],
    "Presidential": [
        ("Serene", 24000, 150, 4, ["Private butler available 24/7", "Rooftop terrace with plunge pool", "In-room spa massage for 2", "Private chef dinner", "Airport pick-up by limousine", "Priority check-in and late check-out"]),
        ("Sapphire", 28000, 180, 4, ["Private cinema room", "Personal wine cellar and champagne welcome", "Dedicated concierge", "Chauffeured luxury car during your stay", "Private gym and sauna", "VIP restaurant reservations"]),
        ("Celestial", 35000, 250, 6, ["Entire top-floor skyline penthouse", "Private elevator access", "Personal chef and butler team", "Full spa suite with therapist on call", "Helipad transfer and security escort", "Exclusive lounge and event hosting"]),
    ],
}
_BLURBS = {key: blurb for key, _title, blurb in TIERS}

# Room photos: the Unsplash photos from the original project, shared out per tier (indexes into _PHOTOS).
# To use your own picture for a room, save it as images/<room name in lowercase>.jpg (e.g. images/luxe.jpg) —
# a local file always wins over the web photo.
_PHOTOS = ["1776763018972-588e27bf6511", "1758448755969-8791367cf5c5", "1788217023349-ad7763845844",
           "1638277000768-005d326db4b2", "1581115685033-ccf1aa701722", "1677129667171-92abd8740fa3"]
_TIER_PHOTOS = {"Executive": [3, 4, 5, 2, 3, 4, 5], "Suite": [1, 0, 2], "Presidential": [0, 1, 0]}
_PHOTO_URL = "https://images.unsplash.com/photo-{}?w=800&h=500&fit=crop&auto=format"

ROOMS = []
for _tier, _rows in _CATALOG.items():
    for _n, (_name, _price, _size, _guests, _amenities) in enumerate(_rows):
        ROOMS.append(dict(
            id=len(ROOMS) + 1, tier=_tier, name=_name, pricePerDay=_price, pricePerHour=int(round(_price * 0.14, -1)),
            size=f"{_size} m²", maxGuests=min(_guests, MAX_GUESTS), image=_name.lower(),
            imageUrl=_PHOTO_URL.format(_PHOTOS[_TIER_PHOTOS[_tier][_n]]), amenities=_amenities, details=_BLURBS[_tier]))

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
    dict(id=1, name="Airport Transfer (one-way)", price=850, image="airport_transfer.png", description="Air-conditioned van, meet & greet service"),
    dict(id=2, name="Laundry Service (per kg)", price=150, image="laundry.png", description="Wash, dry, and fold. Same-day delivery available."),
    dict(id=3, name="In-Room Spa Massage (60 min)", price=1800, image="spa_massage.png", description="Choose from Swedish, Shiatsu, or Hilot"),
    dict(id=4, name="Extra Bed", price=600, image="extra_bed.png", description="Rollaway bed with linens and pillow"),
    dict(id=5, name="Late Checkout (until 3PM)", price=1000, image="late_checkout.png", description="Standard checkout is 12PM noon"),
    dict(id=6, name="Celebration Package", price=2500, image="celebration_package.png", description="Cake, balloons, rose petals, welcome card"),
]


def find_dining_item(item_id: int) -> dict:
    return next(d for d in DINING if d["id"] == item_id)


def find_service_item(item_id: int) -> dict:
    return next(s for s in SERVICES if s["id"] == item_id)