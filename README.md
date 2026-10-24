**La Fleur Sanctuary — HotelBooking System**

# Final-Project

Final Project for CPE009B

## Hotel Booking System (PyQt6)

A desktop hotel booking app built with **PyQt6**. A guest can browse rooms, pick a room, fill in their details, add room service and extra services, choose a payment method, and get a receipt. Prices can be **per day or per hour**, and bookings with a senior or a child get a **10% family discount**.

## Project Structure

```text
hotel_booking_qt/
├── main.py
├── config.py
├── data.py
├── styles.py
├── utils.py
├── widgets/
│   ├── __init__.py
│   └── navbar.py
└── views/
    ├── __init__.py
    ├── base_view.py
    ├── home_view.py
    ├── rooms_view.py
    ├── room_detail_view.py
    ├── booking_view.py
    ├── dining_view.py
    ├── services_view.py
    ├── payment_view.py
    └── receipt_view.py
```
## Program Flow

Home ──► Rooms ──► Room Detail ──┐
 │        │             │        │
 │        └─────────────┴───────► Booking (Step 1)
 │                                  │
 │                                  ▼
 │                                Dining (Step 2)
 │                                  │
 │                                  ▼
 │                                Services (Step 3)
 │                                  │
 │                                  ▼
 │                                Payment (Step 4)
 │                                  │
 │                                  ▼
 └◄──────── Done / Cancel ◄──────── Receipt

 
## How the App Works

Every screen is a **view** stored inside one `QStackedWidget`, and only one view is visible at a time. When a view wants to go somewhere else, it sends a signal with the name of the next view and a small dictionary of data. `main.py` catches that signal, hands the data to the next view, and shows it.

The booking information grows step by step as it moves through the app:

1. Room selection
2. Guest details
3. Dining orders
4. Extra services
5. Payment method

## Main Files

### `main.py`

This is the entry point of the program. It creates the `QApplication`, applies the stylesheet, and builds the main window. The main window holds the navigation bar on top and the `QStackedWidget` below it. It also keeps a dictionary of all eight views and a `navigate()` method that switches between them. Run this file to start the app.

### `config.py`

This file keeps the constants that the whole app shares, so nothing is typed twice. It holds the app title, the window size, the color palette, the tier colors (Premium, Deluxe, Economy), the list of payment methods, the family discount rate (10%), the minimum number of guests (2), and the hotel name, location, and hotline number. If you want to change a color or a rule, you change it here.

### `data.py`

This file holds the sample data that fills the app: the six rooms, the eight dining menu items, and the six add-on services. It has no PyQt code in it. It also has three small helper functions, `find_room()`, `find_dining_item()`, and `find_service_item()`, which look up an item by its ID.

### `styles.py`

This file holds `QSS_STYLE`, the Qt stylesheet that gives the app its dark background and gold look. It styles the buttons, cards, inputs, scroll bars, and labels. It pulls its colors from `config.py`, and it is applied once to the whole app in `main.py`.

### `utils.py`

This file holds the small helper tools used by many views:

- `fmt_currency()` turns a number into peso text like ₱12,500.
- `load_pixmap()` downloads an image from a web link, remembers it so it is not downloaded twice, and shows a plain dark box if the download fails.
- `FlowLayout` is a custom layout that wraps widgets onto the next line when there is no more space. It is used for the amenity tags on the room detail page.

## Widgets Folder

### `widgets/__init__.py`

This file makes `widgets` a package and exports `NavBar`, so `main.py` can write `from widgets import NavBar`.

### `widgets/navbar.py`

This file defines `NavBar`, the bar at the top of every screen. It shows the hotel name, a Rooms link, the location, the hotline, and a **Book a Room** button. It does not switch screens by itself. It only sends three signals (`home_clicked`, `rooms_clicked`, `book_clicked`), and `main.py` decides what to do with them.

## Views Folder

### `views/__init__.py`

This file makes `views` a package and exports all eight view classes, so `main.py` can import them in one line.

### `views/base_view.py`

This file defines `BaseView`, the parent class of every screen. It gives each view the `navigate_to` signal, a short `go()` method for changing screens, and three empty hooks that a view can fill in:

- `on_enter()` runs when data arrives from the previous screen.
- `on_show()` runs after the screen appears.
- `on_leave()` runs when the user moves away.

### `views/home_view.py`

This is the landing page. It shows a hero image with the headline and a **Browse Available Rooms** button, three cards for the Premium, Deluxe, and Economy tiers, and a row of four highlights at the bottom. Clicking a tier card opens the rooms page already filtered to that tier.

### `views/rooms_view.py`

This page shows all the rooms in a grid of cards. The user can switch between per-day and per-hour prices and filter the list by tier. Each card has a **Details** button that opens the room detail page and a **Book** button that goes straight to the booking form.

### `views/room_detail_view.py`

This page shows everything about one room: a large photo, its tier, description, amenity tags, size, maximum guests, and both prices. A **Book This Room** button on the side sends the user to the booking form.

### `views/booking_view.py`

**Step 1 of 4 — Customer and Guest Information**

The user chooses per day or per hour and how long they will stay, enters how many adults, seniors, and children are coming, and types their name, contact number, and email. The price summary on the right updates live, and the 10% discount appears when there is a senior or a child. When the user continues, the form checks that there are at least two guests and that the name, contact, and email are filled in. Errors are shown in a red box.

### `views/dining_view.py`

**Step 2 of 4 — Room Service**

This page shows the room service menu with a category filter. Each dish has plus and minus buttons for the quantity, and an order summary on the right shows the running total. The user can continue with their order or skip this step.

### `views/services_view.py`

**Step 3 of 4 — Add-on Services**

This page shows the add-on services, such as airport transfer, laundry, spa massage, extra bed, late checkout, and celebration package, as cards with quantity buttons. The user can continue or skip.

### `views/payment_view.py`

**Step 4 of 4 — Payment**

The user picks cash, e-wallet, online banking, or card, and the page shows the fields that match the choice. The bill summary on the right lists the room charge, the discount, room service, and add-on services. This file also holds `compute_totals()`, the function that calculates the whole bill, and the receipt page reuses it.

### `views/receipt_view.py`

This is the final page. It builds the receipt with a randomly generated reference number, the date, the guest details, the payment method, every charge, and the total amount due. The **Print** button only shows a message for now, and the **Done** button sends the user back to the home page.
