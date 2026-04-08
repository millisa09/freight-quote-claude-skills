# 🚛 Freight Quote Claude Skills

**Free Claude AI skill pack built specifically for freight brokers.**

Generate branded PDF freight quotes with live EIA diesel surcharge, mileage
calculation, and accessorial tracking — document carrier failures, and
auto-detect RFQ emails — all from inside Claude or Cowork, in seconds.

Built by **[Millisa Nwokolo](https://lacrown.ai)** — 26 years in freight brokerage,
Operations Manager at Finemark Inc., founder of **[La Crown Inc.](https://lacrown.ai)**
— AI automation for freight brokers and logistics professionals.

> _"I built these because I was spending 20 minutes a day formatting the same quote
> PDF. Now it takes 10 seconds. RFQ at 4:18 PM. Signed rate con at 5:07 PM.
> 49 minutes — same hour."_

📺 **[Watch the full build on YouTube](https://youtu.be/EF7pyPDtbak?si=GCoUYJV_X3d6OfiR)**
👥 **[Join the community on Skool](https://skool.com/la-crown-ai-8246)**

---

## What's Inside

| Skill | What It Does | Trigger Phrases |
|---|---|---|
| `freight-quote` | Generates a branded PDF quote with **live EIA diesel**, mileage calc, and accessorial tracking | "quote this load", "make a quote for", "PDF quote" |
| `carrier-incident-report` | Documents carrier failures and drafts carrier + customer emails | "start an incident report", "document this carrier" |
| `rfq-email-scanner` | Scans your Gmail inbox, detects RFQ emails, and drafts quote replies | "check my emails for RFQs", "scan inbox for quotes" |

---

## Quick Install (Under 3 Minutes)

### Step 1 — Install Dependencies

```bash
pip install reportlab requests python-docx
```

### Step 2 — Configure Your Brokerage Info

Copy `config.example.json` → rename it to `config.json` → fill in your details:

```json
{
  "company_name":       "My Brokerage LLC",
  "mc_number":          "MC #123456",
  "address":            "123 Main St, City, ST 00000",
  "email":              "you@yourbrokerage.com",
  "phone":              "555-000-0000",
  "mobile":             "555-000-0001",
  "brand_navy":         "#0D2D5E",
  "brand_gold":         "#C8A84B",
  "valid_days":         14,
  "linehaul_floor":     2.50,
  "fsc_all_inclusive":  true,
  "eia_api_key":        ""
}
```

> You only do this **once**. Every quote, incident report, and email draft will
> automatically use your branding and contact info.
>
> Get a free EIA API key at [eia.gov/opendata/register.php](https://www.eia.gov/opendata/register.php)
> for reliable live diesel data. Leave blank to use the web scraping fallback.

### Step 3 — Use a Skill

Just talk naturally in Claude or Cowork:

```
"Quote this load — origin Chicago IL, destination Dallas TX,
 flatbed, 42,000 lbs, 48x102x6"
```

Claude reads the SKILL.md, runs the scripts, and returns a ready-to-send PDF.

---

## Skill Details

---

### 1. `freight-quote` — PDF Quote Generator with Live EIA Diesel

Generates a professional, fully-branded freight quote PDF from any input —
a pasted email, a load summary, or bullet points.

**What's new in this version:**
- 🛢️ **Live EIA diesel data** — pulls the current week's on-highway diesel price for the correct PADD region automatically. No more quoting on last month's fuel cost.
- 🗺️ **Mileage calculation** — calculates road miles from origin to destination. 100 major freight hubs built in; geocodes anything else automatically.
- 📋 **Accessorial detection** — scans load details and flags tarping, liftgate, detention, layover, permits, and more before you quote.
- 📊 **Lane history aware** — add your past quotes to `config/lane_history.json` and Claude will reference your actual outcomes, not DAT's averaged market data.

**What the PDF includes:**
- Your brokerage header (name, MC#, address, phone, email)
- Quote number, date, valid-until date
- Quoted To section (customer + seller/contact info)
- Shipment Details table (origin, destination, miles, equipment, weight, dims)
- Pricing Summary with live fuel surcharge note (EIA date + diesel price cited)
- Total Flat Rate in your brand color
- Terms & Conditions (8 standard terms auto-included)
- **Cargo Insurance Clause** — carrier covers $100K; shipper must disclose and obtain shipper's interest policy for any value above that limit
- Acceptance / Signature block
- Footer with your contact info

**Live Diesel — PADD Region Auto-Detection:**

| Region | States |
|--------|--------|
| PADD 1 — East Coast | ME, NH, VT, MA, RI, CT, NY, NJ, PA, MD, DE, DC, VA, WV, NC, SC, GA, FL |
| PADD 2 — Midwest | OH, MI, IN, IL, WI, MN, IA, MO, ND, SD, NE, KS, OK, TN, KY |
| PADD 3 — Gulf Coast | TX, LA, MS, AL, AR, NM |
| PADD 4 — Rocky Mountain | MT, ID, WY, CO, UT |
| PADD 5 — West Coast | WA, OR, CA, AK, HI, NV, AZ |

**Accessorials Tracked:**

| Accessorial | When Flagged | Typical Range |
|-------------|--------------|---------------|
| Fuel Surcharge | Every load — live EIA, auto-calculated | Embedded or line item |
| Tarping | Open flatbed + weather protection needed | $75–$200 |
| Liftgate | No dock at receiver | $75–$150 |
| Inside Delivery | Freight past the threshold | $100–$300 |
| Detention | Known slow facility | $65–$100/hr after 2 hrs |
| Layover | Multi-day window or chronic receiver delays | $300–$500/night |
| Oversize Permit | Exceeds 8'6" W, 13'6" H, 53' L, or 80K lbs | $150–$500+/state |
| Driver Assist | Loading/unloading help required | $50–$150/hr |
| Team Driver | Time-critical load | $400–$800 |
| Hazmat | Classified hazardous material | $100–$300 |

**Example input:**
```
Chad from Machinery Futures needs a Conestoga LTL quote.
Origin: Erie PA 16501
Destination: Fishers IN 46037
Machine: 15'L x 4'W x 7'H, 13,000 lbs
```

**Example output:** A polished, ready-to-send PDF with live diesel surcharge noted.
See `/examples/sample-quote.pdf`

---

### 2. `carrier-incident-report` — Carrier Failure Documentation

When a carrier drops the ball, you need to document it fast and professionally.
This skill generates a formal Word document incident report and drafts both a
carrier-facing and customer-facing email.

**Triggers on:**
- Missed delivery appointments
- Driver unreachable / no location updates
- TruckerTools non-compliance
- Cargo damage or shortage
- Driver misrepresenting location
- Detention disputes
- Re-brokering without consent
- Any load where you need a paper trail

**What it produces:**
- Formal incident report (`.docx`) with load #, carrier info, timeline, violation
- Draft email to carrier (firm, professional, documented)
- Draft email to customer (reassuring, factual, protecting your relationship)

---

### 3. `rfq-email-scanner` — Gmail RFQ Detection & Auto-Draft

> ⚠️ **Requires Gmail MCP** to be connected in your Claude/Cowork environment.
> See [INSTALL.md](INSTALL.md) for Gmail MCP setup instructions.

Connects to your Gmail, scans for incoming RFQ / rate request emails,
extracts the load details, and drafts a quote reply — ready for your review
before sending.

**What it detects:**
- Emails with keywords: "quote", "rate", "RFQ", "need a truck", "can you cover", "what's your rate", "pricing for", "freight quote"
- Attachments containing load details
- Replies to existing quote threads asking for updated pricing

**What it produces for each RFQ found:**
- Extracted load details (origin, dest, weight, dims, service type)
- Estimated mileage
- Draft quote reply email (you review before it sends — it never auto-sends)
- Option to generate the full PDF quote in one follow-up command

**Example trigger:**
```
"Scan my inbox for any RFQ emails from today"
"Check my emails for any rate requests"
"Did anyone send me a freight quote request this week?"
```

---

## Standard Cargo Insurance Clause

Every quote generated by this skill pack includes the following clause automatically:

> **Cargo Insurance:** The carrier selected for this shipment will carry a minimum
> of $100,000 in cargo insurance. Any cargo value exceeding $100,000 must be
> disclosed prior to booking. Shipper is responsible for obtaining a shipper's
> interest insurance policy to cover any value above the carrier's cargo liability limit.

---

## File Structure

```
freight-quote-claude-skills/
│
├── README.md                          ← You are here
├── INSTALL.md                         ← Detailed install + Gmail MCP setup
├── LICENSE                            ← MIT — free to use and modify
├── config.example.json                ← Copy → rename → fill in your info
│
├── skills/
│   ├── freight-quote/
│   │   └── SKILL.md                   ← Original quote skill
│   │
│   ├── freight-calculator/            ← NEW — live EIA diesel + mileage + PDF
│   │   ├── SKILL.md                   ← Claude's instruction brain
│   │   ├── config/
│   │   │   └── broker_config.json     ← Your branding (one-time setup)
│   │   ├── scripts/
│   │   │   ├── generate_quote.py      ← PDF generator (ReportLab)
│   │   │   ├── eia_diesel.py          ← Live EIA diesel fetcher by PADD region
│   │   │   └── mileage.py             ← Mileage calculator (100 cities + geocode)
│   │   └── examples/
│   │       └── sample_payload.json    ← Example JSON payload
│   │
│   ├── carrier-incident-report/
│   │   └── SKILL.md
│   │
│   └── rfq-email-scanner/
│       ├── SKILL.md
│       └── scripts/
│           └── scan_rfq.py            ← Gmail scan + extraction logic
│
└── examples/
    └── sample-quote.pdf               ← Example PDF output
```

---

## Requirements

| Requirement | Notes |
|---|---|
| Claude.ai Pro or Team, or Cowork | Skills require Claude access |
| Python 3.8+ | For the PDF generator and scripts |
| `reportlab` | `pip install reportlab` |
| `requests` | `pip install requests` (EIA diesel fetch) |
| `python-docx` | `pip install python-docx` (incident report) |
| Gmail MCP (optional) | Only required for `rfq-email-scanner` |
| EIA API key (optional) | Free at [eia.gov/opendata/register.php](https://www.eia.gov/opendata/register.php) |

---

## Why Not Just Use DAT or FreightWaves?

The SaaS rate platforms average everyone's data together — losses, absorbed
accessorials, distressed carrier rates included. When you quote from their engine,
you're quoting from someone else's mistakes.

This skill pulls **your** data:
- Live EIA diesel for **this week**, not last month
- **Your** lane history and outcomes
- **Your** customer's actual accessorial patterns

> "Stop quoting from someone else's losses." — [Read the full post](https://lacrown.ai/blog)

---

## Want a Custom Build for Your Brokerage?

This free version gives you the foundation. For a **fully custom setup** with:
- Your brokerage's exact branding baked in
- Customer-specific RFQ workflows (repeat shippers, preferred lanes)
- Voice agent integration (callers get quotes automatically)
- Full CRM sync (Close.com, HubSpot, or your TMS)
- Live margin tracking by carrier and customer

👉 Visit **[lacrown.ai](https://lacrown.ai)** or email **millisa@lacrown.ai**

---

## Watch the Build

📺 **[Full video: RFQ to Signed Rate Con in 49 Minutes](https://youtu.be/EF7pyPDtbak?si=GCoUYJV_X3d6OfiR)**
👥 **[Join La Crown's Skool community](https://skool.com/la-crown-ai-8246)**
📰 **[La Crown Blog](https://lacrown.ai/blog)**

---

## Contributing

Found a bug? Have a feature idea? Open an issue or submit a pull request.
This pack is maintained by La Crown Inc. and the freight broker community.

---

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

_Built with 26 years of freight experience and a lot of frustration with
formatting PDFs at 6am. — Missy_
