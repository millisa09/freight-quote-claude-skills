---
name: freight-quote
description: >
  Generate a professional freight broker quote PDF with live EIA diesel surcharge,
  mileage calculation, and accessorial tracking. Trigger on any load request, RFQ,
  rate request, or quote request — even if the user just pastes an email. Extracts
  all load details, fetches live diesel data, calculates miles, identifies
  accessorials, and produces a ready-to-send branded PDF quote.
---

# Freight Quote Skill — Generic Version
**Built by La Crown Inc. | lacrown.ai**

This skill generates a professional freight quote PDF for any freight broker.
It uses live EIA diesel data, mileage calculation, and accessorial detection.
All branding is pulled from `config/broker_config.json` — update that file once
and every quote reflects your company automatically.

---

## Before You Start

1. Read `config/broker_config.json` — load broker name, contact info, MC#, and colors
2. Confirm `scripts/generate_quote.py`, `scripts/eia_diesel.py`, and `scripts/mileage.py` exist
3. Confirm `reportlab` and `requests` are installed (`pip install reportlab requests`)

---

## Step 1 — Extract Load Details

Pull the following from the conversation, email, or pasted text.
Ask only for fields that are genuinely missing and required:

| Field | Required? | Notes |
|-------|-----------|-------|
| Customer / Quoted To | Yes | Company + contact name |
| Requester / Seller | If applicable | Name, company, email, phone |
| Origin | Yes | City, State (ZIP if available) |
| Destination | Yes | City, State (ZIP if available) |
| Commodity | Yes | What is being shipped |
| Weight | Yes | In lbs |
| Dimensions | If available | L × W × H in feet or inches |
| Equipment Type | Yes | Flatbed, Conestoga, Reefer, Van, Step Deck, RGN, etc. |
| Service Type | Yes | FTL, LTL, Partial, Heavy Haul |
| Special Requirements | If mentioned | Tarping, strapping, liftgate, inside delivery, permits |
| Rate | Yes | You will calculate this — see Step 3 |
| Transit Time | Optional | Estimate based on miles if not provided |

---

## Step 2 — Run Mileage Calculation

```bash
python scripts/mileage.py "<origin>" "<destination>"
```

This returns estimated miles using PC Miler-style straight-line calculation with a
road factor. For known lanes from your history, override with actual miles.

Example:
```bash
python scripts/mileage.py "Fort Wayne, IN" "Houston, TX"
# Output: ~1,050 miles
```

---

## Step 3 — Fetch Live EIA Diesel & Calculate Fuel Surcharge

```bash
python scripts/eia_diesel.py "<origin_state_abbr>"
```

This fetches the current week's EIA on-highway diesel price for the correct PADD
region based on origin state. Returns the diesel price and recommended fuel
surcharge percentage from the standard FSC table.

Example:
```bash
python scripts/eia_diesel.py "IN"
# Output: {"padd": "PADD2 - Midwest", "diesel": 5.16, "fsc_pct": 34, "fsc_note": "Based on EIA week of 03/23/2026"}
```

### Fuel Surcharge Table (Standard)

| EIA Diesel ($/gal) | FSC % of Linehaul |
|--------------------|-------------------|
| $2.50 – $2.69 | 12% |
| $2.70 – $2.89 | 15% |
| $2.90 – $3.09 | 18% |
| $3.10 – $3.29 | 21% |
| $3.30 – $3.49 | 24% |
| $3.50 – $3.69 | 27% |
| $3.70 – $3.89 | 30% |
| $3.90 – $4.09 | 33% |
| $4.10 – $4.29 | 36% |
| $4.30 – $4.49 | 39% |
| $4.50 – $4.69 | 42% |
| $4.70 – $4.89 | 45% |
| $4.90 – $5.09 | 48% |
| $5.10 – $5.29 | 51% |
| $5.30 – $5.49 | 54% |
| $5.50 – $5.69 | 57% |
| $5.70 – $5.89 | 60% |
| $5.90 + | 63% |

**Note:** The FSC is calculated on the base linehaul rate, not the total.
For flat-rate quoting (all-inclusive), embed the FSC into the total and note
"Fuel Surcharge Included" in the line items.

---

## Step 4 — Identify Accessorials

Scan the load details for any of the following. Flag each one that applies
and include it in the line items with the appropriate charge:

| Accessorial | When to Flag | Typical Range |
|-------------|--------------|---------------|
| Tarping | Open flatbed + commodity requires weather protection | $75–$200 |
| Strapping / Chains | Heavy machinery, coils, steel | $50–$150 |
| Liftgate | Receiver has no dock | $75–$150 |
| Inside Delivery | Freight must be moved past the threshold | $100–$300 |
| Residential Delivery | Destination is a home or non-commercial address | $75–$150 |
| Driver Assist | Loading/unloading help required | $50–$150/hr |
| Detention | Known slow-loading shipper or receiver | Note: billed if incurred, $65–$100/hr after 2 hrs |
| Layover | Multi-day delivery window or known receiver delays | $300–$500/night |
| Re-consignment | Delivery address change after dispatch | $150–$300 |
| Oversize Permit | Any dimension exceeds: 8'6" W, 13'6" H, 53' L, 80,000 lbs | $150–$500+ per state |
| Escort | Required by state for oversize loads | $200–$500/day |
| Hazmat | Freight is classified hazardous material | $100–$300 |
| Team Driver | Time-critical load requiring continuous driving | $400–$800 |
| Air Ride | Fragile or sensitive cargo | $75–$150 |

**Rule:** If an accessorial is "anticipated but not confirmed," list it as
"Not included — will be billed if incurred" in the terms. Do not pad the
quote with unconfirmed charges.

---

## Step 5 — Build Rate Recommendation

Using miles, fuel surcharge, and accessorials:

```
Base Linehaul     = Miles × (your $/mile floor from config or history)
Fuel Surcharge    = Base Linehaul × FSC%
Accessorials      = Sum of applicable charges
─────────────────────────────────────────
Total All-In Rate = Base + FSC + Accessorials
```

If you have lane history for this origin/destination or customer, reference it
to sanity-check the number before committing. Adjust for market conditions,
customer relationship, and any known carrier availability on the lane.

**Round to the nearest $5 or $25 for cleaner quote presentation.**

---

## Step 6 — Build the JSON Payload

```json
{
  "quote_num": "auto",
  "valid_days": 14,
  "quoted_to": {
    "company": "Customer Company Name",
    "contact": "Contact First Name",
    "seller_name": "Requester Name (if different from customer)",
    "seller_company": "Requester Company",
    "seller_email": "requester@email.com",
    "seller_phone": "555-000-0000"
  },
  "shipment": {
    "origin": "City, ST ZIP",
    "destination": "City, ST ZIP",
    "est_miles": "~X miles",
    "service_type": "e.g. Flatbed FTL",
    "commodity": "Description",
    "equipment": "e.g. Flatbed Trailer",
    "weight": "XX,000 lbs",
    "dimensions": "XX' L × X' W × X' H",
    "permit_class": "Standard",
    "est_transit": "X–X Business Days"
  },
  "line_items": [
    {"description": "Freight Transportation", "notes": "Origin to Destination | ~X miles", "amount": "Included"},
    {"description": "Fuel Surcharge",         "notes": "Live EIA diesel $X.XX/gal (PADD X) — XX% FSC", "amount": "Included"},
    {"description": "Accessorial: [Name]",    "notes": "Description",                                    "amount": "$XXX"},
    {"description": "Accessorial Charges",    "notes": "None anticipated (see terms)",                    "amount": "—"}
  ],
  "total_label": "TOTAL FLAT RATE",
  "total_note": "All-inclusive | No hidden fees",
  "total_amount": "$X,XXX.00",
  "extra_terms": []
}
```

---

## Step 7 — Generate the PDF

```bash
python scripts/generate_quote.py examples/sample_payload.json
```

Or pass JSON inline:
```bash
python scripts/generate_quote.py '<paste json here>'
```

The script outputs the full path to the generated PDF file.

---

## Step 8 — Present the File

After the script runs, share the PDF with the user. Provide a brief summary:
- Customer, origin → destination
- Total rate
- Fuel surcharge basis (EIA date + diesel price)
- Any accessorials flagged
- Quote validity date

---

## Rate History (Optional but Powerful)

Add a `config/lane_history.json` file to track past quotes and outcomes:

```json
[
  {
    "customer": "Acme Corp",
    "origin": "Chicago, IL",
    "destination": "Dallas, TX",
    "equipment": "Flatbed",
    "miles": 921,
    "quoted": 2850,
    "accepted": true,
    "carrier_cost": 2400,
    "margin": 450,
    "accessorials_billed": 0,
    "notes": "Smooth load, no issues"
  }
]
```

When a new RFQ comes in for a similar lane, Claude will reference this history
to anchor the rate recommendation in real outcomes — not market averages.

---

## Rules for Every Quote

- Always use **this week's EIA diesel** — never last week's, never an estimate
- Always calculate **actual miles** — never round-number guesses
- Always identify accessorials **from the load description** — never assume none
- Always include the **cargo insurance clause** in terms (built into generator)
- Never promise a rate without flagging **potential accessorials** in the terms
- Fuel surcharge note in line items must always cite **the EIA date and diesel price**
- Quote validity is **14 days** by default — adjust in config if needed

---

## Config Reference

See `config/broker_config.json` for:
- Company name, MC#, address, phone, email
- Brand colors (hex)
- Default valid_days
- Default FSC table override (if you use a different scale)
- Default linehaul floor ($/mile)

---

## Support & Community

- **Watch the full build:** [youtube.com/@lacrown_ai](https://youtube.com/@lacrown_ai)
- **Join the community:** [skool.com/la-crown-ai-8246](https://skool.com/la-crown-ai-8246)
- **More skills:** [lacrown.ai](https://lacrown.ai)
