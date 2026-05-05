---
name: test-multitruck-quote
description: >
  TEST/DEMO skill — generates a multi-truck / multi-option heavy haul freight quote PDF
  using fictional brokerage info (Apex Transit LLC, MC #123456) so the workflow can be
  recorded for social media (YouTube, LinkedIn, Twitter, Skool) without exposing real
  Finemark or customer details. Demonstrates the Option 1 (separate trucks) vs Option 2
  (combined oversize) pricing layout, heavy haul/superload terminology, escort and permit
  callouts, and "QUOTED RATES: $X / $Y" total format. Trigger phrases: "test multi-truck
  quote", "demo multi-truck quote", "demo heavy haul quote", "test option quote", "show
  me the option quote demo", "build a multi-truck demo", "fake multi-truck quote", "demo
  the option layout", "sandbox multi-truck", "test the multi-truck quoter", "demo the
  heavy haul format", "build a heavy haul demo for social", or any time a multi-truck
  heavy haul quote is needed for recording, screenshots, or skill testing. Always
  produces a ready-to-download PDF stamped with TEST/DEMO notices throughout. Never use
  for real customers — use finemark-rfq for live work.
---

# Test Multi-Truck Quote — Heavy Haul Option Pricing Generator (DEMO MODE)

Generates a fully formatted multi-truck / multi-option freight quote PDF using
**Apex Transit LLC** (fictional brokerage, MC #123456) in place of any real
company details. Built specifically for the "Option 1 vs Option 2" heavy haul
scenario — splitting one disassembled machine across multiple trucks with a
combined-oversize alternative.

Identical layout and logic to the live multi-truck quote workflow — safe for
social media demos, YouTube recordings, LinkedIn screenshots, and skill development.

---

## Fake Brokerage Reference

| Field        | Value                                  |
|--------------|---------------------------------------|
| Company      | APEX TRANSIT LLC                       |
| MC #         | 123456                                 |
| Address      | PO Box 4400, Indianapolis, IN 46201    |
| Phone        | 317-555-0192                           |
| Mobile       | 317-555-0847                           |
| Email        | quotes@apextransit.com                 |
| Contact      | Alex Rivera                            |
| Quote Prefix | ATQ-YYYY-MMDD                          |
| Output File  | ApexTransit_MultiTruck_[Cust].pdf      |

---

## Two Trigger Modes

### Mode A — "Just run the demo"
If the user says any of: "run the demo", "show me the multi-truck demo",
"build the heavy haul demo", "just run it", or doesn't provide any specific
load details — use the **built-in default scenario** below. This is the fastest
path for recording video content.

### Mode B — "Demo this specific load"
If the user provides specific load details (origin, destination, commodity,
weights, dimensions, prices), use those instead of the defaults. Still uses
Apex Transit branding and TEST/DEMO stamps.

---

## Built-In Default Scenario (Mode A)

A fictional industrial blow molder shipment — generic enough for any social
media context, specific enough to demonstrate the full workflow:

| Field        | Value                                                              |
|--------------|--------------------------------------------------------------------|
| Customer     | Continental Industrial Group                                        |
| Contact      | Pat Morgan                                                          |
| Email        | pat.morgan@continentalindustrial.com                                |
| Origin       | Springfield, MA                                                     |
| Destination  | Toledo, OH                                                          |
| Est. Miles   | ~625 miles                                                          |
| Service Type | Heavy Haul / Multi-Truck Specialized                                |
| Commodity    | Industrial Blow Molder (disassembled) — frame, top deck w/ extruders, clamping unit, blow molder heads & components |
| Equipment    | Step Decks + Heavy Haul + Box Trailer (multi-truck)                 |
| Permit Class | Heavy Haul / Oversize (Truck #3 + Option 2 Trucks #1/#2)            |
| Est. Transit | 4–6 Business Days (subject to permit windows)                       |

### Default Pricing Structure (intentionally different from real Finemark numbers)

**OPTION 1 — Four (4) Separate Trucks**
| # | Description                          | Specs                                                              | Amount     |
|---|--------------------------------------|--------------------------------------------------------------------|------------|
| 1 | Frame + misc. pallets                | 13' W × 24' L × 9' T \| legal weight \| Step Deck                 | $3,400.00  |
| 2 | Top Deck w/ Extruders                | 13' W × 24' L × 6' T \| legal weight \| Step Deck                 | $3,400.00  |
| 3 | Clamping Unit                        | 11' W × 18' L × 11'5" T \| 92,000 lbs \| Heavy Haul + permits + escorts | $17,200.00 |
| 4 | Blow Molder Heads + Parts            | Box Trailer \| heads + components, palletized                      | $2,800.00  |
|   | **OPTION 1 SUBTOTAL**                | **Four (4) trucks — all-in**                                       | **$26,800.00** |

**OPTION 2 — Three (3) Trucks (Trucks #1 + #2 Combined)**
| # | Description                          | Specs                                                              | Amount     |
|---|--------------------------------------|--------------------------------------------------------------------|------------|
| 1+2 | Combined oversize load             | 13'3"–13'6" W × 24' L × 12'3" T \| 40,000 lbs \| escorts + permits | $11,200.00 |
| 3 | Clamping Unit                        | 11' W × 18' L × 11'5" T \| 92,000 lbs \| Heavy Haul + permits + escorts | $16,900.00 |
| 4 | Blow Molder Heads + Parts            | Box Trailer \| heads + components, palletized                      | $2,800.00  |
|   | **OPTION 2 SUBTOTAL**                | **Three (3) trucks — all-in**                                      | **$30,900.00** |

**QUOTED RATES**: $26,800 / $30,900 (Customer to select Option 1 or Option 2 prior to booking)

---

## Step 1 — Build Quote Number

Format: `ATQ-YYYY-MMDD`
Use today's date. If a second quote on the same day, append a letter: `ATQ-2026-0505B`

---

## Step 2 — Run the PDF Generator

The generator is bundled at `scripts/generate_quote.py`.
**Copy it to /home/claude/ before running** (skill directory is read-only):

```bash
cp /mnt/skills/user/test-multitruck-quote/scripts/generate_quote.py /home/claude/generate_multitruck_test.py
```

Build the JSON payload and run:

```bash
python /home/claude/generate_multitruck_test.py '<JSON>'
```

### JSON Template

```json
{
  "quote_num": "ATQ-YYYY-MMDD",
  "valid_days": 14,
  "quoted_to": {
    "company": "Continental Industrial Group",
    "contact": "Pat Morgan",
    "seller_email": "pat.morgan@continentalindustrial.com"
  },
  "shipment": {
    "origin": "Springfield, MA",
    "destination": "Toledo, OH",
    "est_miles": "~625 miles",
    "service_type": "Heavy Haul / Multi-Truck Specialized",
    "commodity": "Industrial Blow Molder (disassembled) — frame, top deck w/ extruders, clamping unit, blow molder heads & components",
    "equipment": "Step Decks + Heavy Haul + Box Trailer (multi-truck)",
    "weight": "Mixed — see truck-by-truck breakdown below",
    "permit_class": "Heavy Haul / Oversize (Truck #3 + Option 2 Trucks #1/#2)",
    "dimensions": "Multi-truck — varies by unit (see breakdown below)",
    "est_transit": "4–6 Business Days (subject to permit windows)"
  },
  "line_items": [
    {"description": "<b>OPTION 1 — Four (4) Separate Trucks</b>", "notes": "<i>Each unit shipped on its own trailer</i>", "amount": ""},
    {"description": "Truck #1 — Frame + misc. pallets",          "notes": "13' W × 24' L × 9' T | legal weight, full load | Step Deck",                  "amount": "$3,400.00"},
    {"description": "Truck #2 — Top Deck w/ Extruders",          "notes": "13' W × 24' L × 6' T | legal weight, full load | Step Deck",                  "amount": "$3,400.00"},
    {"description": "Truck #3 — Clamping Unit",                  "notes": "11' W × 18' L × 11'5\" T | 92,000 lbs | Heavy Haul w/ permits & escorts",     "amount": "$17,200.00"},
    {"description": "Truck #4 — Blow Molder Heads + Parts",      "notes": "Box Trailer | heads + components, palletized",                                "amount": "$2,800.00"},
    {"description": "<b>OPTION 1 SUBTOTAL</b>",                  "notes": "<b>Four (4) trucks — all-in</b>",                                              "amount": "<b>$26,800.00</b>"},
    {"description": "<b>OPTION 2 — Three (3) Trucks</b><br/><b>(Trucks #1 + #2 Combined)</b>", "notes": "<i>Trucks #1 and #2 ride together as one oversize load</i>", "amount": ""},
    {"description": "Trucks #1 + #2 (Combined)",                 "notes": "13'3\"–13'6\" W × 24' L × 12'3\" T | 40,000 lbs | Includes escorts & permits", "amount": "$11,200.00"},
    {"description": "Truck #3 — Clamping Unit",                  "notes": "11' W × 18' L × 11'5\" T | 92,000 lbs | Heavy Haul w/ permits & escorts",     "amount": "$16,900.00"},
    {"description": "Truck #4 — Blow Molder Heads + Parts",      "notes": "Box Trailer | heads + components, palletized",                                "amount": "$2,800.00"},
    {"description": "<b>OPTION 2 SUBTOTAL</b>",                  "notes": "<b>Three (3) trucks — all-in</b>",                                             "amount": "<b>$30,900.00</b>"}
  ],
  "total_label": "QUOTED RATES",
  "total_note": "Customer to select Option 1 or Option 2 prior to booking",
  "total_amount": "$26,800 / $30,900",
  "extra_terms": [
    "Two pricing options provided. Option 1 ($26,800) ships four separate legal-weight loads. Option 2 ($30,900) combines Trucks #1 + #2 into a single 12'3\"-tall oversize load with required escorts and permits.",
    "Truck #3 (Clamping Unit, 92,000 lbs) ships Heavy Haul on a multi-axle trailer. State-issued superload/heavy haul permits and escort vehicles are included in the quoted rate. Routing is subject to state DOT approval; pickup and delivery dates are tentative until permits are issued.",
    "Option 2 combined load (12'3\" T × 13'6\" W) requires height and width permits across all transit states. Front and/or rear escort vehicles are included. Daylight-only travel may be required by certain states.",
    "Trucks #1, #2, and #4 ship on standard step deck or box trailer equipment at legal weight and dimensions.",
    "Loading and unloading must be performed by the shipper and consignee using their own equipment and personnel. Driver will assist with strapping, tarping, and securement only.",
    "Quoted dimensions and weights are based on shipper-provided specifications. Any variance discovered at pickup may result in a rate adjustment, particularly on Truck #3 and the Option 2 combined load.",
    "Final delivery address required prior to dispatch. Rate assumes standard commercial dock or yard delivery with adequate maneuvering space for oversize equipment.",
    "All trucks ship as a coordinated multi-load shipment. Pickup window will be scheduled to align all four (or three) trucks within the same 24–48 hour window where feasible."
  ]
}
```

**Seller block**: If no seller info is provided, pass empty strings for all seller fields —
the generator suppresses the seller block automatically.

**HTML formatting in line_items**: The `description`, `notes`, and `amount` fields render
as ReportLab Paragraphs and support `<b>`, `<i>`, and `<br/>` tags. Use these for option
headers and bold subtotal rows.

---

## Step 3 — Output Filename

`ApexTransit_MultiTruck_[CustomerName].pdf`

Rules:
- Remove spaces and special characters from customer name
- If buyer is TBD: `ApexTransit_MultiTruck_TBD.pdf`

---

## Step 4 — Present the File

After the script runs, call `present_files` with the output path.
Then give a brief bullet summary:
- Quote # and valid-through date
- Buyer (Apex Transit fictional context)
- Lane (Origin → Destination, ~miles)
- Both Option 1 and Option 2 rates
- Reminder: this is a TEST/DEMO document using Apex Transit LLC (fictional)

---

## Document Notices

The generated PDF includes two built-in demo notices that **cannot be removed**:
- Top banner: `*** TEST / DEMO DOCUMENT — NOT FOR CUSTOMER USE ***`
- Footer line: `*** TEST DOCUMENT — FICTIONAL BROKERAGE — DO NOT DISTRIBUTE ***`

This makes the PDF safe to share publicly on social media, in YouTube videos,
LinkedIn posts, Twitter/X content, or Skool community lessons.

---

## Social Media Use Cases

This skill is built for:
- **YouTube tutorials** showing how Claude builds branded freight quotes
- **LinkedIn posts** demonstrating AI-powered brokerage workflows
- **Twitter/X threads** showcasing freight tech automation
- **Skool community** lessons inside La Crown AI
- **Screen recordings** for sales demos to other brokerages
- **Internal testing** before shipping changes to the live finemark-rfq skill

Never use for live customer work. For real Finemark quotes, use `finemark-rfq` instead.
