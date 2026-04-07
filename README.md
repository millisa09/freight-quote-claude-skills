# 🚛 Freight Quote Claude Skills

**Free Claude AI skill pack built specifically for freight brokers.**

Generate branded PDF freight quotes, document carrier failures, and auto-detect
RFQ emails — all from inside Claude or Cowork, in seconds.

Built by **[Millisa Nwokolo](https://lacrown.ai)** — 26 years in freight brokerage,
Operations Manager at Finemark Inc., founder of **[La Crown Inc.](https://lacrown.ai)**
— AI automation for freight brokers and logistics professionals.

> _"I built these because I was spending 20 minutes a day formatting the same quote
> PDF. Now it takes 10 seconds."_

---

## What's Inside

| Skill | What It Does | Trigger Phrases |
|---|---|---|
| `freight-quote` | Generates a branded PDF freight quote from any load details or email | "quote this load", "make a quote for", "PDF quote" |
| `carrier-incident-report` | Documents carrier failures and drafts carrier + customer emails | "start an incident report", "document this carrier" |
| `rfq-email-scanner` | Scans your Gmail inbox, detects RFQ emails, and drafts quote replies | "check my emails for RFQs", "scan inbox for quotes" |

---

## Quick Install (Under 3 Minutes)

### Step 1 — Configure Your Brokerage Info

Copy `config.example.json` → rename it to `config.json` → fill in your details:

```json
{
  "broker_company":       "My Brokerage LLC",
  "broker_mc":            "MC #123456",
  "broker_address":       "123 Main St, City, ST 00000",
  "broker_email":         "you@yourbrokerage.com",
  "broker_phone_office":  "555-000-0000",
  "broker_phone_mobile":  "555-000-0001",
  "broker_contact_name":  "Your Name",
  "brand_color_navy":     "#0D2D5E",
  "brand_color_gold":     "#C8A84B",
  "quote_prefix":         "FMQ",
  "default_valid_days":   14
}
```

> You only do this **once**. Every quote you generate will automatically use your
> branding and contact info.

### Step 2 — Download a Skill File

Go to the [Releases](../../releases) tab and download the `.skill` file(s) you want.

### Step 3 — Install in Cowork or Claude

1. Open **Cowork** or **Claude.ai**
2. Go to **Settings → Skills → Upload Skill**
3. Upload the `.skill` file
4. Done ✅

### Step 4 — Use It

Just talk naturally:

```
"Quote this load — origin Chicago IL, destination Dallas TX,
 flatbed, 42,000 lbs, 48x102, $1,850"
```

Claude will build and return a ready-to-send PDF quote in your branding.

---

## Skill Details

---

### 1. `freight-quote` — PDF Quote Generator

Generates a professional, fully-branded freight quote PDF from any input:
a pasted email, a load summary, or bullet points.

**What the PDF includes:**
- Your brokerage header (name, MC#, address, phone, email)
- Quote number, date, valid-until date
- Quoted To section (customer + seller/contact info)
- Shipment Details table (origin, destination, miles, equipment, weight, dims)
- Pricing Summary table with line items
- Total Flat Rate with your amount in your brand color
- Terms & Conditions (8 standard terms auto-included)
- **Cargo Insurance Clause** — carrier covers $100K; shipper must disclose
  and obtain shipper's interest policy for any value above that limit
- Acceptance / Signature block
- Footer with your contact info

**Example input:**

```
Seth from Machinery Network needs a Conestoga LTL quote.
Origin: Trumbauersville PA 18970
Destination: Mahtomedi MN 55115
Machine: 15'L x 4'W x 7'H, 13,000 lbs
Quote: $3,185
```

**Example output:** A polished, ready-to-send PDF — see `/examples/sample-quote.pdf`

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

This skill connects to your Gmail, scans for incoming RFQ / rate request emails,
extracts the load details, and drafts a quote reply — ready for your review before
sending.

**What it detects:**
- Emails with keywords: "quote", "rate", "RFQ", "need a truck", "can you cover",
  "what's your rate", "pricing for", "freight quote"
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

Every quote generated by this skill pack includes the following clause,
which protects you as the broker:

> **Cargo Insurance:** The carrier selected for this shipment will carry a minimum
> of $100,000 in cargo insurance. Any cargo value exceeding $100,000 must be
> disclosed prior to booking. Shipper is responsible for obtaining a shipper's
> interest insurance policy to cover any value above the carrier's cargo liability
> limit.

This is included automatically on every quote. You do not need to add it manually.

---

## Customizing Your Brand Colors

The PDF generator supports any brand colors. Update `config.json`:

```json
{
  "brand_color_navy": "#0D2D5E",
  "brand_color_gold": "#C8A84B"
}
```

Use any hex color codes that match your brokerage brand. The generator will apply
them to your company name, quote title, total amount, and section dividers.

---

## File Structure

```
freight-quote-claude-skills/
│
├── README.md                         ← You are here
├── INSTALL.md                        ← Detailed install + Gmail MCP setup
├── LICENSE                           ← MIT — free to use and modify
├── config.example.json               ← Copy this → rename → fill in your info
│
├── skills/
│   ├── freight-quote/
│   │   ├── SKILL.md                  ← Skill instructions for Claude
│   │   └── scripts/
│   │       └── generate_quote.py    ← PDF generator (Python / ReportLab)
│   │
│   ├── carrier-incident-report/
│   │   └── SKILL.md
│   │
│   └── rfq-email-scanner/
│       ├── SKILL.md
│       └── scripts/
│           └── scan_rfq.py          ← Gmail scan + extraction logic
│
├── examples/
│   └── sample-quote.pdf             ← Example output so you know what to expect
│
└── releases/
    ├── freight-quote.skill
    ├── carrier-incident-report.skill
    └── rfq-email-scanner.skill
```

---

## Requirements

| Requirement | Notes |
|---|---|
| Claude.ai Pro or Team, or Cowork | Skills require Claude access |
| Python 3.8+ | For the PDF generator script |
| `reportlab` Python library | `pip install reportlab` |
| `python-docx` Python library | `pip install python-docx` (incident report) |
| Gmail MCP (optional) | Only required for `rfq-email-scanner` |

> In Cowork and Claude.ai's built-in environment, Python and libraries are
> pre-installed. You only need to install manually if running locally.

---

## Want a Custom Build for Your Brokerage?

This free version gives you the foundation. For a **fully custom setup** with:
- Your brokerage's exact branding
- Customer-specific RFQ workflows (Kelly Pipe, repeat shippers, etc.)
- Voice agent integration (callers get quotes automatically)
- Full CRM sync (Close.com, HubSpot, or your TMS)

👉 Visit **[lacrown.ai](https://lacrown.ai)** or email **missy@finemarkgroup.com**

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
