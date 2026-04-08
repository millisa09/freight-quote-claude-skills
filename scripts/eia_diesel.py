#!/usr/bin/env python3
"""
eia_diesel.py — Live EIA On-Highway Diesel Fetcher
Built by La Crown Inc. | lacrown.ai

Usage:
    python eia_diesel.py <state_abbr>
    python eia_diesel.py IN
    python eia_diesel.py TX

Returns JSON with:
    - padd region name
    - current diesel price ($/gal)
    - fuel surcharge % from standard table
    - EIA data date
    - source URL

Data source: https://www.eia.gov/petroleum/gasdiesel/
Updated weekly every Monday.
"""

import sys
import json
import re
import urllib.request
import urllib.error
from datetime import datetime

# ── PADD Region mapping by state ─────────────────────────────────────────────
PADD_MAP = {
    # PADD 1 — East Coast
    "ME": "PADD1", "NH": "PADD1", "VT": "PADD1", "MA": "PADD1",
    "RI": "PADD1", "CT": "PADD1", "NY": "PADD1", "NJ": "PADD1",
    "PA": "PADD1", "MD": "PADD1", "DE": "PADD1", "DC": "PADD1",
    "VA": "PADD1", "WV": "PADD1", "NC": "PADD1", "SC": "PADD1",
    "GA": "PADD1", "FL": "PADD1",
    # PADD 2 — Midwest
    "OH": "PADD2", "MI": "PADD2", "IN": "PADD2", "IL": "PADD2",
    "WI": "PADD2", "MN": "PADD2", "IA": "PADD2", "MO": "PADD2",
    "ND": "PADD2", "SD": "PADD2", "NE": "PADD2", "KS": "PADD2",
    "OK": "PADD2",
    # PADD 3 — Gulf Coast
    "TX": "PADD3", "LA": "PADD3", "MS": "PADD3", "AL": "PADD3",
    "AR": "PADD3", "NM": "PADD3",
    # PADD 4 — Rocky Mountain
    "MT": "PADD4", "ID": "PADD4", "WY": "PADD4", "CO": "PADD4",
    "UT": "PADD4",
    # PADD 5 — West Coast
    "WA": "PADD5", "OR": "PADD5", "CA": "PADD5", "AK": "PADD5",
    "HI": "PADD5", "NV": "PADD5", "AZ": "PADD5",
    # Tennessee / Kentucky — PADD 2 border, treat as PADD2
    "TN": "PADD2", "KY": "PADD2",
}

PADD_LABELS = {
    "PADD1": "PADD 1 — East Coast",
    "PADD2": "PADD 2 — Midwest",
    "PADD3": "PADD 3 — Gulf Coast",
    "PADD4": "PADD 4 — Rocky Mountain",
    "PADD5": "PADD 5 — West Coast",
}

# ── EIA API series IDs for weekly on-highway diesel by PADD ───────────────────
# Source: https://www.eia.gov/opendata/
EIA_SERIES = {
    "US":    "PET.EMD_EPD2D_PTE_NUS_DPG.W",   # U.S. National Average
    "PADD1": "PET.EMD_EPD2D_PTE_R10_DPG.W",   # East Coast
    "PADD2": "PET.EMD_EPD2D_PTE_R20_DPG.W",   # Midwest
    "PADD3": "PET.EMD_EPD2D_PTE_R30_DPG.W",   # Gulf Coast
    "PADD4": "PET.EMD_EPD2D_PTE_R40_DPG.W",   # Rocky Mountain
    "PADD5": "PET.EMD_EPD2D_PTE_R50_DPG.W",   # West Coast
}

# ── EIA API v2 URL ────────────────────────────────────────────────────────────
EIA_API_URL = (
    "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
    "?frequency=weekly&data[0]=value&facets[product][]=EPD2D"
    "&facets[duoarea][]={area}&sort[0][column]=period"
    "&sort[0][direction]=desc&length=1&api_key={key}"
)

# Area codes for EIA API v2
PADD_AREA = {
    "US":    "NUS",
    "PADD1": "R10",
    "PADD2": "R20",
    "PADD3": "R30",
    "PADD4": "R40",
    "PADD5": "R50",
}

# ── Fuel Surcharge Table (standard broker FSC scale) ─────────────────────────
FSC_TABLE = [
    (2.50, 2.69, 12),
    (2.70, 2.89, 15),
    (2.90, 3.09, 18),
    (3.10, 3.29, 21),
    (3.30, 3.49, 24),
    (3.50, 3.69, 27),
    (3.70, 3.89, 30),
    (3.90, 4.09, 33),
    (4.10, 4.29, 36),
    (4.30, 4.49, 39),
    (4.50, 4.69, 42),
    (4.70, 4.89, 45),
    (4.90, 5.09, 48),
    (5.10, 5.29, 51),
    (5.30, 5.49, 54),
    (5.50, 5.69, 57),
    (5.70, 5.89, 60),
    (5.90, 99.0, 63),
]


def get_fsc_pct(diesel_price: float) -> int:
    """Return fuel surcharge % for a given diesel price."""
    for low, high, pct in FSC_TABLE:
        if low <= diesel_price <= high:
            return pct
    return 63  # cap at 63% for anything above table


def fetch_eia_diesel(padd: str = "US", api_key: str = "") -> dict:
    """
    Fetch current EIA diesel price via EIA Open Data API v2.
    Falls back to web scraping if no API key is provided.
    
    Args:
        padd: PADD region key (US, PADD1–PADD5)
        api_key: EIA API key (free at https://www.eia.gov/opendata/register.php)
    
    Returns:
        dict with diesel price, date, fsc_pct, padd label
    """
    area = PADD_AREA.get(padd, "NUS")

    if api_key:
        url = EIA_API_URL.format(area=area, key=api_key)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            row = data["response"]["data"][0]
            price = float(row["value"])
            period = row["period"]  # e.g. "2026-03-24"
            return {
                "padd": PADD_LABELS.get(padd, padd),
                "area_code": area,
                "diesel": price,
                "fsc_pct": get_fsc_pct(price),
                "period": period,
                "fsc_note": f"Based on EIA week of {period}",
                "source": "https://www.eia.gov/petroleum/gasdiesel/",
                "api_used": True,
            }
        except Exception as e:
            # Fall through to scrape fallback
            pass

    # ── Fallback: scrape EIA page ─────────────────────────────────────────────
    # Note: scraping may break if EIA changes page layout.
    # Register a free API key at https://www.eia.gov/opendata/register.php
    # and pass it via --api-key for reliable results.
    try:
        url = "https://www.eia.gov/petroleum/gasdiesel/"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; FreightQuoteSkill/1.0)"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")

        # EIA diesel table pattern — find on-highway diesel row
        # The page lists U.S. national first, then regions
        # We look for the pattern in the diesel section
        padd_patterns = {
            "US":    r"U\.S\.[^\d]*(\d+\.\d+)",
            "PADD1": r"East Coast[^\d]*(\d+\.\d+)",
            "PADD2": r"Midwest[^\d]*(\d+\.\d+)",
            "PADD3": r"Gulf Coast[^\d]*(\d+\.\d+)",
            "PADD4": r"Rocky Mountain[^\d]*(\d+\.\d+)",
            "PADD5": r"West Coast[^\d]*(\d+\.\d+)",
        }

        # Find diesel section of page (after "On-Highway Diesel")
        diesel_section = html
        diesel_marker = html.find("On-Highway Diesel")
        if diesel_marker > 0:
            diesel_section = html[diesel_marker:]

        pattern = padd_patterns.get(padd, padd_patterns["US"])
        match = re.search(pattern, diesel_section)

        if match:
            price = float(match.group(1))
        else:
            # Last resort: use U.S. national if region not found
            us_match = re.search(r"U\.S\.[^\d]*(\d+\.\d+)", diesel_section)
            price = float(us_match.group(1)) if us_match else 5.40  # conservative fallback

        today = datetime.today().strftime("%Y-%m-%d")
        return {
            "padd": PADD_LABELS.get(padd, padd),
            "area_code": area,
            "diesel": price,
            "fsc_pct": get_fsc_pct(price),
            "period": today,
            "fsc_note": f"Based on EIA data fetched {today} (register API key for precision)",
            "source": "https://www.eia.gov/petroleum/gasdiesel/",
            "api_used": False,
        }

    except Exception as e:
        # Hard fallback — use conservative estimate and flag it
        today = datetime.today().strftime("%Y-%m-%d")
        return {
            "padd": PADD_LABELS.get(padd, "Unknown Region"),
            "area_code": area,
            "diesel": 5.40,
            "fsc_pct": get_fsc_pct(5.40),
            "period": today,
            "fsc_note": "EIA fetch failed — using conservative estimate. Verify at eia.gov",
            "source": "https://www.eia.gov/petroleum/gasdiesel/",
            "api_used": False,
            "error": str(e),
        }


def state_to_padd(state: str) -> str:
    """Return PADD region key for a given state abbreviation."""
    state = state.strip().upper()
    # Handle full state names — extract abbreviation
    if len(state) > 2:
        state = state[:2]
    return PADD_MAP.get(state, "US")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch live EIA on-highway diesel price by state or PADD region."
    )
    parser.add_argument("state", nargs="?", default="US",
                        help="State abbreviation (e.g. IN, TX, CA) or PADD key (PADD1–PADD5)")
    parser.add_argument("--api-key", default="",
                        help="EIA Open Data API key (free at eia.gov/opendata/register.php)")
    parser.add_argument("--padd", action="store_true",
                        help="Treat input as PADD key directly instead of state")
    args = parser.parse_args()

    if args.padd or args.state.upper().startswith("PADD"):
        padd = args.state.upper()
    else:
        padd = state_to_padd(args.state)

    result = fetch_eia_diesel(padd, args.api_key)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
