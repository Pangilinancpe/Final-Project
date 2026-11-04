"""
database.py — SQLite storage for confirmed bookings (standard library only, no PyQt).

hotel.db is created next to this file on first run (DB_PATH below) and every confirmed booking is written to that file. Three tables:
  bookings        one row per confirmed booking (guest/payer contacts, payment, totals)
  guests          one row per guest name        (linked to its booking)
  booking_items   room-service dishes and add-on services ordered (linked to its booking)
Deleting a booking also deletes its guests and items (ON DELETE CASCADE).
"""

import csv
import os
import random
import sqlite3
import string
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
    reference TEXT PRIMARY KEY, created_at TEXT NOT NULL,
    room_id INTEGER, room_name TEXT, room_tier TEXT, pricing_mode TEXT, duration INTEGER,
    adults INTEGER, seniors INTEGER, children INTEGER, child_ages TEXT,
    contact TEXT, email TEXT, payer_name TEXT, payer_contact TEXT,
    payment_method TEXT, payment_provider TEXT, payment_account_name TEXT, payment_account_ref TEXT,
    room_charge REAL, discount REAL, dining_total REAL, services_total REAL, grand_total REAL);
CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL REFERENCES bookings(reference) ON DELETE CASCADE, full_name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS booking_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL REFERENCES bookings(reference) ON DELETE CASCADE,
    kind TEXT NOT NULL, name TEXT NOT NULL, unit_price REAL NOT NULL, qty INTEGER NOT NULL);
"""


def make_reference() -> str:
    """Random reference number like HB-7K2P9XQ4."""
    return "HB-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with closing(_connect()) as conn, conn:
        conn.executescript(SCHEMA)


def save_booking(b: dict, totals: dict) -> None:
    """Save one confirmed booking (the dict built by the booking flow) and its guests/items in one transaction."""
    room, g, pay, cust, payer = b["room"], b["guests"], b["payment"], b["customer"], b["payer"]
    row = dict(
        reference=b["reference"], created_at=b["createdAt"].isoformat(timespec="seconds"),
        room_id=room["id"], room_name=room["name"], room_tier=room["tier"],
        pricing_mode=b["pricingMode"], duration=b["duration"],
        adults=g["adults"], seniors=g["seniors"], children=g["children"], child_ages=", ".join(map(str, b["childAges"])),
        contact=cust["contact"], email=cust["email"], payer_name=payer["name"], payer_contact=payer["contact"],
        payment_method=pay["method"], payment_provider=pay.get("provider"),
        payment_account_name=pay.get("accountName"), payment_account_ref=pay.get("accountRef"),
        room_charge=totals["base"], discount=totals["discount"], dining_total=totals["dining_total"],
        services_total=totals["svc_total"], grand_total=totals["grand_total"])
    items = [(b["reference"], kind, e["item"]["name"], e["item"]["price"], e["qty"])
             for kind, key in (("dining", "dining"), ("service", "extraServices")) for e in b[key]]
    with closing(_connect()) as conn, conn:
        conn.execute(f"INSERT INTO bookings ({', '.join(row)}) VALUES ({', '.join(':' + k for k in row)})", row)
        conn.executemany("INSERT INTO guests (reference, full_name) VALUES (?, ?)", [(b["reference"], n) for n in b["guestNames"]])
        conn.executemany("INSERT INTO booking_items (reference, kind, name, unit_price, qty) VALUES (?, ?, ?, ?, ?)", items)


def list_bookings() -> list:
    """All bookings, newest first, each with a 'guest_names' string."""
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT b.*, (SELECT group_concat(full_name, ', ') FROM guests g WHERE g.reference = b.reference)"
                            " AS guest_names FROM bookings b ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


EXPORT_COLUMNS = ("reference", "created_at", "guest_names", "contact", "email", "payer_name", "payer_contact", "room_name",
                  "room_tier", "pricing_mode", "duration", "adults", "seniors", "children", "payment_method",
                  "payment_provider", "payment_account_name", "payment_account_ref", "room_charge", "discount",
                  "dining_total", "services_total", "grand_total")


def export_csv(path: str) -> int:
    """Save every booking to a .csv file (opens in Excel). Returns how many rows were written."""
    rows = list_bookings()
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig so Excel shows the peso sign correctly
        writer = csv.DictWriter(f, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def delete_booking(reference: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM bookings WHERE reference = ?", (reference,))
