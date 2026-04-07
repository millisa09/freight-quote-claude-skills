---
name: freight-quote
description: >
  Generate a professional branded freight quote PDF for any load. Use this skill
  whenever someone asks for a freight quote, rate quote, shipping quote, or any
  quote to send to a customer or shipper — even if they just paste an email or
  say "quote this load." Also trigger on: "make a quote for", "send a quote to",
  "put together a quote", "need a PDF quote", "create a quote for [customer/load]",
  "quote this", or when load details are pasted with a dollar amount. This skill
  reads your brokerage config and produces a ready-to-send branded PDF every time.
  Never attempt to build the PDF from scratch without reading this skill first.
---

# Freight Quote — PDF Generator

Produces a professional, branded freight quote PDF from any load input.
Reads broker info from `config.json` — one setup, every quote branded automatically.

---

## Step 1 — Load Config

Before generating, read the broker's `config.json` to get branding and contact info.
Look for it in the skill folder. If it doesn't exist, ask the user to set it up
by copying `config.example.json` → `config.json` and filling in their details.

Required fields from config:
- `broker_company`, `broker_mc`, `broker_address`
- `broker_email`, `broker_phone_office`, `broker_phone_mobile`, `broker_contact_name`
- `brand_color_navy`, `brand_color_gold`
- `quote_prefix`, `default_valid_days`

---

## Step 2 — Extract Quote Data

Pull the following from the conversation. Ask only for fields that are missing
and genuinely needed to produce a useful quote:

| Field | Required | Notes |
|---|---|---|
| Customer / Quoted To | Yes | Company name + contact name |
| Seller / Requested By | If applicable | Name, company, email, phone |
| Origin | Yes | City, State ZIP |
| Destination | Yes | City, State ZIP |
| Commodity | Yes | What is being shipped |
| Weight | Yes | In lbs |
| Dimensions | Yes | L x W x H |
| Service Type | Yes | Flatbed, Conestoga LTL, Heavy Haul, Reefer, Van, etc. |
| Quoted Rate | Yes | Dollar amount |
| Estimated Miles | Optional | Estimate if not given |
| Est. Transit | Optional | e.g. 3–5 Business Days |
| Equipment | Optional | Specific trailer type |
| Permit Class | Optional | Standard / Overweight / Over-Dimensional |
| Extra line items | Optional | Permits, escorts, etc. |
| Extra terms | Optional | Anything beyond the 8 standard terms |

---

## Step 3 — Build JSON and Run Generator

Once you have all required fields, run the bundled script:

```bash
python skills/freight-quote/scripts/generate_quote.py '<JSON>' '<CONFIG_PATH>'
```

Pass the config file path as the second argument.
The script outputs the PDF file path on success.

### JSON Payload Structure

```json
{
  "quote_num": "FMQ-2026-0407",
  "valid_days": 14,
  "quoted_to": {
    "company": "Customer Company Name",
    "contact": "Contact Name",
    "address": "123 Street, City, ST 00000",
    "phone": "555-000-0000",
    "seller_name": "Seller Name, Title",
    "seller_company": "Seller Company",
    "seller_email": "seller@example.com",
    "seller_phone": "555-000-0001"
  },
  "shipment": {
    "origin": "City, ST ZIP",
    "destination": "City, ST ZIP",
    "est_miles": "~1,200 miles",
    "service_type": "Conestoga LTL",
    "commodity": "Industrial Machinery",
    "equipment": "Conestoga Trailer",
    "weight": "13,000 lbs",
    "permit_class": "Standard",
    "dimensions": "15' L x 4' W x 7' H",
    "est_transit": "3–5 Business Days"
  },
  "line_items": [
    {"description": "Freight Transportation", "notes": "Origin to Destination | ~1,200 miles", "amount": "Included"},
    {"description": "Fuel Surcharge",          "notes": "Included in flat rate",               "amount": "Included"},
    {"description": "Accessorial Charges",     "notes": "None anticipated (see notes)",        "amount": "—"}
  ],
  "total_label": "TOTAL FLAT RATE",
  "total_note": "All-inclusive | No hidden fees",
  "total_amount": "$1,850.00",
  "extra_terms": []
}
```

`extra_terms` is optional — add strings to append after the 8 standard terms.

---

## Step 4 — Present the File

After the script runs, call `present_files` with the output path.
Give a brief summary: lane, service type, quoted amount, valid through date.

---

## Output Filename Convention

`FreightQuote_[CustomerSlug]_[ServiceSlug].pdf`

e.g. `FreightQuote_AcmeCorp_Flatbed.pdf`

---

## The 8 Standard Terms (auto-included — do not remove)

1. Payment due in full prior to scheduling pickup.
2. Quote valid for N days (date range shown).
3. Rate applies to service type noted — no inside delivery, liftgate, or residential surcharges unless specified.
4. Shipper responsible for blocking, bracing, and securing freight.
5. Dimensional/weight discrepancies may result in rate adjustment.
6. Detention, driver-assist, re-consignment billed separately if incurred.
7. Broker operates as licensed freight broker — carrier selection at discretion.
8. **Cargo Insurance:** Carrier carries minimum $100,000. Shipper must disclose value above $100K and obtain shipper's interest insurance policy.
