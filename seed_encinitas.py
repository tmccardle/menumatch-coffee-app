"""Load Encinitas coffee rows through the running API.

Run while python app.py is up:

    python seed_encinitas.py
"""
from __future__ import print_function

import json
import os
try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import Request, urlopen, HTTPError, URLError

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE = os.environ.get("MENU_API_BASE", "http://localhost:8000")
WRITE_KEY = os.environ.get("MENU_WRITE_KEY", "")

SHOPS = [
    {
        "name": "Pannikin Coffee",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "510 N Coast Hwy 101, Encinitas",
        "website": "https://www.pannikincoffeeandtea.com/",
        "title": "Coffee menu",
        "raw_menu": {"items": [
            {"name": "Drip coffee", "price": 4.50},
            {"name": "Espresso", "price": 3.50},
            {"name": "Cafe au lait", "price": 4.75},
            {"name": "Banana bread", "price": 3.75, "kind": "food"},
            {"name": "Avocado toast", "price": 9.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "classic cafe", "setting": "railroad station"},
    },
    {
        "name": "Ironsmith Coffee Roasters",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "458 S Coast Hwy 101, Encinitas",
        "website": "https://www.ironsmithcoffee.com/",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.50},
            {"name": "Flat white", "price": 5.25},
            {"name": "Pour over", "price": 5.50},
            {"name": "New wave bagel", "price": 8.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "single-origin", "setting": "roaster cafe"},
    },
    {
        "name": "Necessity Coffee",
        "city": "Encinitas",
        "area": "Leucadia",
        "address": "687 2nd St, Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "House drip", "price": 3.75},
            {"name": "Cortado", "price": 4.50},
            {"name": "Batch brew", "price": 4.00},
            {"name": "Seasonal pastry", "price": 4.25, "kind": "food"},
            {"name": "Cardamom latte", "price": 5.75},
        ]},
        "characterization": {"roast": "light-medium", "style": "specialty", "setting": "hidden studio"},
    },
    {
        "name": "Bump Coffee",
        "city": "Encinitas",
        "area": "Cardiff",
        "address": "1302 N Coast Hwy 101, Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Latte", "price": 5.50},
            {"name": "Cold brew", "price": 5.00},
            {"name": "Matcha", "price": 5.75},
            {"name": "Breakfast burrito", "price": 10.50, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "espresso bar", "setting": "patio"},
    },
    {
        "name": "Coffee Coffee",
        "city": "Encinitas",
        "area": "Leucadia",
        "address": "970 N Coast Hwy 101, Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Americano", "price": 4.00},
            {"name": "Oat latte", "price": 5.75},
            {"name": "Granola bowl", "price": 9.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "cafe", "setting": "patio"},
    },
    {
        "name": "Lofty Coffee Encinitas",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "Encinitas Roasting Works",
        "website": "https://loftycoffee.com/",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Drip", "price": 3.50},
            {"name": "Cappuccino", "price": 5.00},
            {"name": "Almond croissant", "price": 5.50, "kind": "food"},
        ]},
        "characterization": {"roast": "light", "style": "roaster", "setting": "roasting works"},
    },
    {
        "name": "Bird Rock Coffee Roasters",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "Encinitas",
        "website": "https://www.birdrockcoffee.com/",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.75},
            {"name": "Filter", "price": 5.00},
            {"name": "Cardamom bun", "price": 4.50, "kind": "food"},
        ]},
        "characterization": {"roast": "light-medium", "style": "third wave", "setting": "roaster cafe"},
    },
    {
        "name": "Para Cafe",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "949 2nd St, Encinitas",
        "website": "",
        "title": "Cafe menu",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.50},
            {"name": "Oat latte", "price": 5.50},
            {"name": "Iced latte", "price": 5.75},
            {"name": "Breakfast sandwich", "price": 9.50, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "neighborhood cafe", "setting": "walk-up"},
    },
    {
        "name": "E.S.B. Cafe",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "325 Encinitas Blvd, Encinitas",
        "website": "",
        "title": "Cafe menu",
        "raw_menu": {"items": [
            {"name": "Fresh brew", "price": 3.50},
            {"name": "Oat latte", "price": 5.50},
            {"name": "Iced mocha latte", "price": 5.75},
            {"name": "Ham Swiss sandwich", "price": 9.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "walk-up cafe", "setting": "side street"},
    },
    {
        "name": "Fourtillfour Cafe",
        "city": "Encinitas",
        "area": "Leucadia",
        "address": "1114 N Coast Hwy 101, Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.75},
            {"name": "Latte", "price": 5.50},
            {"name": "Pour over", "price": 5.50},
            {"name": "Pastry", "price": 4.50, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "roaster cafe", "setting": "patio"},
    },
    {
        "name": "Crossings Coffee Roasters",
        "city": "Encinitas",
        "area": "Leucadia",
        "address": "312 N Coast Hwy 101, Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.50},
            {"name": "Cortado", "price": 4.50},
            {"name": "Batch brew", "price": 4.00},
        ]},
        "characterization": {"roast": "light-medium", "style": "micro-roaster", "setting": "Leucadia shop"},
    },
    {
        "name": "Sip-N-Sea",
        "city": "Encinitas",
        "area": "Leucadia",
        "address": "1488 N Coast Hwy 101, Encinitas",
        "website": "",
        "title": "Coffee and bowls",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.50},
            {"name": "Hazelnut fudge latte", "price": 5.75},
            {"name": "Vanilla gold brew", "price": 5.00},
            {"name": "Acai bowl", "price": 12.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "beach cafe", "setting": "Coast Highway"},
    },
    {
        "name": "Queenstage",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "Encinitas",
        "website": "",
        "title": "Drinks",
        "raw_menu": {"items": [
            {"name": "Espresso", "price": 3.50},
            {"name": "Latte", "price": 5.50},
            {"name": "Drip", "price": 3.75},
        ]},
        "characterization": {"roast": "medium", "style": "cyclist cafe", "setting": "near 101"},
    },
    {
        "name": "Surfdog's Java Hut",
        "city": "Encinitas",
        "area": "Downtown",
        "address": "1126 S Coast Hwy 101, Encinitas",
        "website": "http://www.surfdogjavahut.com/",
        "title": "Cafe menu",
        "raw_menu": {"items": [
            {"name": "Drip coffee", "price": 3.50},
            {"name": "Latte", "price": 5.25},
            {"name": "Espresso", "price": 3.25},
            {"name": "Bacon egg cheese bagel", "price": 10.00, "kind": "food"},
            {"name": "Quesadilla", "price": 8.00, "kind": "food"},
        ]},
        "characterization": {"roast": "medium", "style": "surf cafe", "setting": "101 shack"},
    },
]


def call(method, path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = Request(BASE + path, data=data, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if method != "GET" and WRITE_KEY:
        req.add_header("X-Menu-Key", WRITE_KEY)
    try:
        res = urlopen(req)
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else None
    except HTTPError as err:
        detail = err.read().decode("utf-8")
        raise SystemExit("HTTP %s %s %s\n%s" % (err.code, method, path, detail))
    except URLError as err:
        raise SystemExit("Cannot reach %s (%s). Start python app.py first." % (BASE, err.reason))


def existing_rows():
    rows = call("GET", "/menus/restaurants") or []
    by_name = {}
    for row in rows:
        if isinstance(row, dict) and row.get("name"):
            by_name[row["name"].strip().lower()] = row
    return by_name


def ensure_menu_id(row, shop):
    menus = row.get("menus") or []
    if menus and menus[0].get("id"):
        return menus[0]["id"]
    menu = call("POST", "/menus/", {
        "restaurant_id": row["id"],
        "title": shop["title"],
    })
    return menu["id"]


def main():
    have = existing_rows()
    created = 0
    updated = 0
    for shop in SHOPS:
        key = shop["name"].strip().lower()
        if key in have:
            menu_id = ensure_menu_id(have[key], shop)
            call("POST", "/menus/versions", {
                "menu_id": menu_id,
                "raw_menu": shop["raw_menu"],
                "characterization": shop["characterization"],
            })
            print("updated menu:", shop["name"])
            updated += 1
            continue
        restaurant = call("POST", "/menus/restaurants", {
            "name": shop["name"],
            "city": shop["city"],
            "area": shop["area"],
            "address": shop.get("address"),
            "website": shop.get("website") or None,
        })
        menu = call("POST", "/menus/", {
            "restaurant_id": restaurant["id"],
            "title": shop["title"],
        })
        call("POST", "/menus/versions", {
            "menu_id": menu["id"],
            "raw_menu": shop["raw_menu"],
            "characterization": shop["characterization"],
        })
        print("added:", shop["name"])
        created += 1
    print("done. added %s, updated %s" % (created, updated))


if __name__ == "__main__":
    main()
