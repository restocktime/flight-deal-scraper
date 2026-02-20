#!/usr/bin/env python3
"""
Flight Deal Scraper — Kiwi Tequila API (free tier)
Scans routes, finds cheapest deals, outputs clean results + booking links.

Get your free API key at: https://tequila.kiwi.com/portal/login
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

TEQUILA_API = "https://api.tequila.kiwi.com/v2"
API_KEY = ""  # Paste your key here, or use env var KIWI_API_KEY

HEADERS = {"apikey": API_KEY}


def search_flights(fly_from, fly_to, date_from=None, date_to=None,
                   nights_from=2, nights_to=14, max_results=10, max_price=None, currency="USD"):
    if not date_from:
        date_from = datetime.now().strftime("%d/%m/%Y")
    if not date_to:
        date_to = (datetime.now() + timedelta(days=60)).strftime("%d/%m/%Y")

    params = {
        "fly_from": fly_from,
        "fly_to": fly_to,
        "date_from": date_from,
        "date_to": date_to,
        "nights_in_dst_from": nights_from,
        "nights_in_dst_to": nights_to,
        "flight_type": "round",
        "one_for_city": 0,
        "adults": 1,
        "curr": currency,
        "sort": "price",
        "limit": max_results,
        "max_stopovers": 1,
    }
    if max_price:
        params["price_to"] = max_price

    try:
        resp = requests.get(f"{TEQUILA_API}/search", headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        if resp.status_code == 401:
            print("ERROR: API key not set or invalid.")
            print("Get free key: https://tequila.kiwi.com/portal/login")
        else:
            print(f"HTTP {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_flight(flight):
    price = flight.get("price", 0)
    outbound, inbound = [], []
    for route in flight.get("route", []):
        leg = {
            "from": route.get("flyFrom", ""),
            "to": route.get("flyTo", ""),
            "airline": route.get("airline", ""),
            "departure": route.get("local_departure", "")[:16],
            "arrival": route.get("local_arrival", "")[:16],
        }
        (inbound if route.get("return") else outbound).append(leg)

    return {
        "price": f"${price}",
        "price_raw": price,
        "from": flight.get("cityFrom", ""),
        "to": flight.get("cityTo", ""),
        "outbound_date": outbound[0]["departure"] if outbound else "",
        "return_date": inbound[0]["departure"] if inbound else "",
        "outbound_stops": len(outbound) - 1,
        "inbound_stops": len(inbound) - 1,
        "airlines": list(set(r.get("airline", "") for r in flight.get("route", []))),
        "booking_link": flight.get("deep_link", ""),
    }


def print_results(results, label=""):
    if not results or not results.get("data"):
        print(f"  No flights found for {label}")
        return []

    flights = results["data"]
    print(f"\n{'='*60}")
    print(f"  {label} — {len(flights)} deals")
    print(f"{'='*60}")

    formatted = []
    for i, f in enumerate(flights[:10]):
        d = format_flight(f)
        formatted.append(d)
        stops_out = "direct" if d["outbound_stops"] == 0 else f"{d['outbound_stops']} stop"
        stops_in = "direct" if d["inbound_stops"] == 0 else f"{d['inbound_stops']} stop"
        airlines = ", ".join(d["airlines"])
        print(f"\n  #{i+1}  {d['price']}")
        print(f"  OUT: {d['outbound_date']}  ({stops_out})")
        print(f"  RET: {d['return_date']}  ({stops_in})")
        print(f"  Airlines: {airlines}")
        print(f"  Book: {d['booking_link'][:100]}...")

    return formatted


def scan_deals(routes, date_from=None, date_to=None, max_price=None, output_file="latest-flight-deals.json"):
    print(f"\n  FLIGHT DEAL SCANNER")
    print(f"  Scanning {len(routes)} routes | Dates: {date_from or 'next 60 days'}")
    if max_price:
        print(f"  Max price: ${max_price}")

    all_deals = []
    for fly_from, fly_to, label in routes:
        results = search_flights(fly_from, fly_to, date_from, date_to, max_price=max_price)
        deals = print_results(results, label)
        for d in deals[:5]:
            d["route"] = label
            all_deals.append(d)

    all_deals.sort(key=lambda x: x["price_raw"])

    print(f"\n{'='*60}")
    print(f"  TOP 10 CHEAPEST ACROSS ALL ROUTES")
    print(f"{'='*60}")
    for i, d in enumerate(all_deals[:10]):
        print(f"  #{i+1}  {d['price']:>8}  {d['route']}")
        print(f"         {d['outbound_date']} — {d['return_date']}")

    # Save results
    with open(output_file, "w") as f:
        json.dump(all_deals[:20], f, indent=2)
    print(f"\n  Saved top 20 deals to {output_file}")

    return all_deals


# ============================================
# EXAMPLE ROUTES — customize these!
# (departure_IATA, destination_IATA, "Label")
# ============================================
EXAMPLE_ROUTES = [
    ("MIA", "TLV", "Miami → Tel Aviv"),
    ("MIA", "BCN", "Miami → Barcelona"),
    ("MIA", "CDG", "Miami → Paris"),
    ("MIA", "LHR", "Miami → London"),
    ("MIA", "FCO", "Miami → Rome"),
    ("MIA", "CUN", "Miami → Cancun"),
    ("MIA", "SJO", "Miami → Costa Rica"),
    ("MIA", "BOG", "Miami → Bogota"),
    ("MIA", "LIS", "Miami → Lisbon"),
    ("MIA", "ATH", "Miami → Athens"),
]


if __name__ == "__main__":
    key = os.environ.get("KIWI_API_KEY", "") or API_KEY
    if len(sys.argv) > 1 and not sys.argv[1].isdigit():
        key = sys.argv[1]

    if not key:
        print("=" * 60)
        print("  FLIGHT DEAL SCRAPER — SETUP")
        print("=" * 60)
        print()
        print("  1. Go to https://tequila.kiwi.com/portal/login")
        print("  2. Sign up free (30 sec)")
        print("  3. Create a Solution → copy API key")
        print("  4. Run: KIWI_API_KEY=your_key python3 flight_scraper.py")
        print("     Or:  python3 flight_scraper.py your_key")
        print("     Or:  paste key on line 16 of this script")
        sys.exit(0)

    HEADERS["apikey"] = key
    max_p = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            max_p = int(arg)

    scan_deals(EXAMPLE_ROUTES, max_price=max_p)
