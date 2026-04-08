#!/usr/bin/env python3
"""
mileage.py — Freight Mileage Calculator
Built by La Crown Inc. | lacrown.ai

Usage:
    python mileage.py "Fort Wayne, IN" "Houston, TX"
    python mileage.py "Chicago, IL 60601" "Dallas, TX 75201"

Returns JSON with:
    - estimated miles
    - calculation method used
    - origin/destination confirmed

Note: For exact PC Miler results, use the PC Miler API or TruckMiles API.
This script uses a geodesic (great-circle) calculation with a road factor
of 1.22 — a standard approximation used in freight brokerage.

For high-volume or high-value loads, always verify with your TMS.
"""

import sys
import json
import math
import re
import urllib.request
import urllib.parse
import argparse

# ── Road factor: multiply straight-line miles by this to approximate road miles
# Industry standard approximation for freight brokerage
ROAD_FACTOR = 1.22

# ── City coordinate database for common freight lanes ─────────────────────────
# Populated with major freight hubs — for other cities, falls back to geocoding
CITY_COORDS = {
    "CHICAGO, IL":        (41.8781, -87.6298),
    "HOUSTON, TX":        (29.7604, -95.3698),
    "DALLAS, TX":         (32.7767, -96.7970),
    "LOS ANGELES, CA":    (34.0522, -118.2437),
    "ATLANTA, GA":        (33.7490, -84.3880),
    "NEW YORK, NY":       (40.7128, -74.0060),
    "FORT WAYNE, IN":     (41.0793, -85.1394),
    "INDIANAPOLIS, IN":   (39.7684, -86.1581),
    "COLUMBUS, OH":       (39.9612, -82.9988),
    "CLEVELAND, OH":      (41.4993, -81.6944),
    "DETROIT, MI":        (42.3314, -83.0458),
    "MEMPHIS, TN":        (35.1495, -90.0490),
    "NASHVILLE, TN":      (36.1627, -86.7816),
    "CHARLOTTE, NC":      (35.2271, -80.8431),
    "PHILADELPHIA, PA":   (39.9526, -75.1652),
    "PHOENIX, AZ":        (33.4484, -112.0740),
    "SAN ANTONIO, TX":    (29.4241, -98.4936),
    "SAN DIEGO, CA":      (32.7157, -117.1611),
    "SAN JOSE, CA":       (37.3382, -121.8863),
    "JACKSONVILLE, FL":   (30.3322, -81.6557),
    "AUSTIN, TX":         (30.2672, -97.7431),
    "SAN FRANCISCO, CA":  (37.7749, -122.4194),
    "COLUMBUS, GA":       (32.4610, -84.9877),
    "CHARLOTTE, MI":      (42.5636, -84.8358),
    "DENVER, CO":         (39.7392, -104.9903),
    "EL PASO, TX":        (31.7619, -106.4850),
    "SEATTLE, WA":        (47.6062, -122.3321),
    "BOSTON, MA":         (42.3601, -71.0589),
    "LOUISVILLE, KY":     (38.2527, -85.7585),
    "PORTLAND, OR":       (45.5051, -122.6750),
    "LAS VEGAS, NV":      (36.1699, -115.1398),
    "MILWAUKEE, WI":      (43.0389, -87.9065),
    "ALBUQUERQUE, NM":    (35.0844, -106.6504),
    "TUCSON, AZ":         (32.2540, -110.9742),
    "FRESNO, CA":         (36.7378, -119.7871),
    "SACRAMENTO, CA":     (38.5816, -121.4944),
    "KANSAS CITY, MO":    (39.0997, -94.5786),
    "MESA, AZ":           (33.4152, -111.8315),
    "OMAHA, NE":          (41.2565, -95.9345),
    "MINNEAPOLIS, MN":    (44.9778, -93.2650),
    "MIAMI, FL":          (25.7617, -80.1918),
    "ORLANDO, FL":        (28.5383, -81.3792),
    "TAMPA, FL":          (27.9506, -82.4572),
    "CINCINNATI, OH":     (39.1031, -84.5120),
    "PITTSBURGH, PA":     (40.4406, -79.9959),
    "RICHMOND, VA":       (37.5407, -77.4360),
    "ST. LOUIS, MO":      (38.6270, -90.1994),
    "BALTIMORE, MD":      (39.2904, -76.6122),
    "RALEIGH, NC":        (35.7796, -78.6382),
    "GREENVILLE, SC":     (34.8526, -82.3940),
    "BIRMINGHAM, AL":     (33.5186, -86.8104),
    "SALT LAKE CITY, UT": (40.7608, -111.8910),
    "BOISE, ID":          (43.6150, -116.2023),
    "SPOKANE, WA":        (47.6588, -117.4260),
    "LITTLE ROCK, AR":    (34.7465, -92.2896),
    "JACKSON, MS":        (32.2988, -90.1848),
    "BATON ROUGE, LA":    (30.4515, -91.1871),
    "NEW ORLEANS, LA":    (29.9511, -90.0715),
    "OKLAHOMA CITY, OK":  (35.4676, -97.5164),
    "TULSA, OK":          (36.1540, -95.9928),
    "WICHITA, KS":        (37.6872, -97.3301),
    "SIOUX FALLS, SD":    (43.5446, -96.7311),
    "FARGO, ND":          (46.8772, -96.7898),
    "BILLINGS, MT":       (45.7833, -108.5007),
    "CHEYENNE, WY":       (41.1400, -104.8197),
    "COLORADO SPRINGS, CO": (38.8339, -104.8214),
    "ALLENTOWN, PA":      (40.6084, -75.4902),
    "HARRISBURG, PA":     (40.2732, -76.8867),
    "TRENTON, NJ":        (40.2171, -74.7429),
    "BUFFALO, NY":        (42.8864, -78.8784),
    "ALBANY, NY":         (42.6526, -73.7562),
    "HARTFORD, CT":       (41.7658, -72.6851),
    "PROVIDENCE, RI":     (41.8240, -71.4128),
    "PORTLAND, ME":       (43.6591, -70.2568),
    "BURLINGTON, VT":     (44.4759, -73.2121),
    "MANCHESTER, NH":     (42.9956, -71.4548),
    "SPRINGFIELD, MA":    (42.1015, -72.5898),
    "WORCESTER, MA":      (42.2626, -71.8023),
    "BRIDGEPORT, CT":     (41.1865, -73.1952),
    "NEWARK, NJ":         (40.7357, -74.1724),
}

def normalize_city(raw: str) -> str:
    """Normalize a city string to 'CITY, ST' format for lookup."""
    raw = raw.strip().upper()
    # Remove ZIP codes
    raw = re.sub(r'\b\d{5}(?:-\d{4})?\b', '', raw).strip().strip(',').strip()
    # Collapse extra spaces
    raw = re.sub(r'\s+', ' ', raw)
    return raw


def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    """Calculate great-circle distance in miles between two lat/lon points."""
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def geocode_nominatim(location: str) -> tuple:
    """
    Geocode a location using OpenStreetMap Nominatim (free, no API key).
    Returns (lat, lon) tuple or raises ValueError.
    """
    encoded = urllib.parse.quote(location + ", USA")
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1&countrycodes=us"
    req = urllib.request.Request(url, headers={
        "User-Agent": "FreightQuoteSkill/1.0 (lacrown.ai)"
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        results = json.loads(r.read().decode())
    if not results:
        raise ValueError(f"Could not geocode: {location}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def get_coords(location: str) -> tuple:
    """
    Get coordinates for a location.
    First checks built-in city database, then falls back to Nominatim geocoding.
    """
    normalized = normalize_city(location)

    # Direct lookup
    if normalized in CITY_COORDS:
        return CITY_COORDS[normalized], normalized, "database"

    # Try partial match (city only, ignoring state)
    city_only = normalized.split(',')[0].strip() if ',' in normalized else normalized
    for key, coords in CITY_COORDS.items():
        if key.startswith(city_only + ","):
            return coords, key, "database_partial"

    # Geocode fallback
    try:
        coords = geocode_nominatim(location)
        return coords, location, "geocoded"
    except Exception as e:
        raise ValueError(f"Cannot locate '{location}': {e}")


def calculate_miles(origin: str, destination: str) -> dict:
    """
    Calculate estimated road miles between origin and destination.
    Returns dict with miles, method, and location info.
    """
    try:
        (lat1, lon1), origin_label, origin_method = get_coords(origin)
        (lat2, lon2), dest_label, dest_method = get_coords(destination)

        straight_miles = haversine_miles(lat1, lon1, lat2, lon2)
        road_miles = round(straight_miles * ROAD_FACTOR)

        # Round to nearest 5 for cleaner display
        road_miles_display = round(road_miles / 5) * 5

        return {
            "origin": origin_label,
            "destination": dest_label,
            "straight_line_miles": round(straight_miles),
            "road_miles": road_miles_display,
            "road_factor": ROAD_FACTOR,
            "display": f"~{road_miles_display:,} miles",
            "method": f"Geodesic × {ROAD_FACTOR} road factor",
            "origin_method": origin_method,
            "dest_method": dest_method,
            "note": "Verify with TMS for high-value or permit loads",
        }

    except ValueError as e:
        return {
            "origin": origin,
            "destination": destination,
            "road_miles": None,
            "display": "Unable to calculate — enter miles manually",
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate estimated freight road miles between two points."
    )
    parser.add_argument("origin", help='Origin location, e.g. "Fort Wayne, IN"')
    parser.add_argument("destination", help='Destination location, e.g. "Houston, TX"')
    args = parser.parse_args()

    result = calculate_miles(args.origin, args.destination)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
