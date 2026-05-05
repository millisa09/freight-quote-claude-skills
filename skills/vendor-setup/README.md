# Vendor Setup Packet Skill — Customization README

A drop-in Claude Skill that generates branded vendor setup packets (W-9 + banking info) for any freight brokerage, agency, or service business. Comes pre-loaded with a fictional brand (Apex Transit LLC) so you can test the workflow safely, then customize with your own info to ship the real version.

**Time to customize: ~20 minutes.**

---

## What You're Customizing

You're forking the `test-vendor-setup` skill and turning it into your own live vendor packet generator. When you're done, anyone on your team can type *"send my W9 and banking to Faye at ECINTL"* and get a branded 2-page PDF in seconds.

You'll edit:

1. **Company info** — legal name, EIN, address, MC #
2. **Banking info** — bank name, routing, account, remittance email
3. **Contact info** — primary contact, phone, email
4. **Brand identity** — colors, tagline, logo wordmark
5. **Trigger phrases** — so it fires on your company name
6. **W-9 file** — swap in your signed PDF

Three files total. No coding required for most edits — just find-and-replace.

---

## Before You Start

**Prerequisites:**
- Your signed W-9 saved as a PDF
- Your banking info (routing #, account #, bank name)
- Two brand colors (primary + accent) — hex codes
- A short tagline (optional)

**File locations:** Everything you need to edit lives in two files:

```
your-vendor-setup/
├── SKILL.md              ← edit triggers + description
└── assets/
    ├── build_packet.py   ← edit constants + colors
    └── signed_w9.pdf     ← replace with your real W-9
```

---

## Step 1 — Rename the Skill

Open `SKILL.md`. The first line of the frontmatter is the skill name.

**Change this:**
```yaml
name: test-vendor-setup
```

**To something descriptive for your business:**
```yaml
name: yourcompany-vendor-setup
```

Use lowercase, hyphens only, no spaces. Examples:
- `acme-vendor-setup`
- `northstar-vendor-packet`
- `riverside-ap-onboarding`

Also rename the parent folder to match.

---

## Step 2 — Update the Description (Trigger Phrases)

Still in `SKILL.md`, the `description` field tells Claude when to fire the skill. **This is the most important field to customize** — wrong triggers means the skill never fires, or fires when you don't want it to.

**The 1024-character limit is hard.** Your description must fit within it. Count characters before saving.

### Template to Adapt

```yaml
description: >
  Generate a polished, branded [YOUR COMPANY] Vendor Setup Packet PDF whenever a
  customer's AP team requests our W-9, banking, or remittance info for vendor
  onboarding. Output is a 2-page PDF: branded cover sheet with company info,
  banking, and operating details, followed by our signed W-9. ALWAYS trigger when
  [YOUR NAME] says any of: "vendor setup packet", "vendor onboarding", "set me
  up as a vendor", "set up [YOUR COMPANY] as a vendor", "send my W9 and banking",
  "send the W9 and ACH", "AP wants my W9", "AP needs my W9", "send remit info",
  or any time a forwarded email from an AP/Accounts Payable contact requests W-9
  + banking/ACH/remittance info. NEVER send a bare W-9 if banking was also
  requested — always run this skill so both go in one branded packet. Run
  end-to-end in one shot: pull the requester's contact info from email if needed,
  build the PDF, present it, and offer a draft reply.
```

**Replace** `[YOUR COMPANY]` and `[YOUR NAME]` with actual values, then **count characters** before saving.

### Quick character count check

```bash
python3 -c "
desc = '''paste your full description here'''
print('Length:', len(desc))
print('Under 1024?', len(desc) <= 1024)
"
```

If you go over 1024, trim duplicate trigger phrases first ("vendor onboarding packet" and "vendor info packet" are redundant — keep one).

---

## Step 3 — Edit Your Brand Constants

Open `assets/build_packet.py`. Near the top of the file, find this block:

```python
# =====================================================================
# FAKE BRAND CONSTANTS — clearly fictional, safe for demos
# =====================================================================
APEX = {
    "legal_name":        "APEX TRANSIT LLC",
    "ein":               "99-1234567",
    "tax_class":         "LLC (Partnership)",
    "mailing_address":   "PO Box 4400, Indianapolis, IN 46201",
    "mc_number":         "123456",
    ...
}
```

**Rename `APEX` to your company name** (use a short variable name in caps, like `ACME`, `NORTHSTAR`, etc.) and **replace every value** with your real info:

```python
# =====================================================================
# COMPANY CONSTANTS — edit here if any of this changes
# =====================================================================
ACME = {
    "legal_name":        "ACME LOGISTICS LLC",
    "ein":               "12-3456789",
    "tax_class":         "S Corporation",     # see options below
    "mailing_address":   "123 Main St., Your City, ST 12345",
    "mc_number":         "1234567",
    "bank_name":         "First National Bank  —  Your City, ST",
    "account_name":      "Acme Logistics LLC  (Business Checking)",
    "routing":           "021000021",         # your real ABA routing
    "account":           "1234567890",        # your real account #
    "remit_email":       "remit@acmelogistics.com",
    "primary_contact":   "Jane Doe, Operations Manager",
    "phones":            "555-123-4567 (office)  |  555-987-6543 (mobile)",
    "payment_terms":     "Net 30 from invoice date",
    "tagline":           "Your Tagline Here.",
    "website":           "www.acmelogistics.com",
    "office_email":      "jane@acmelogistics.com",
}
```

### Tax classification options

Use the exact string that matches your W-9:

| Your W-9 box | Use this string |
|--------------|-----------------|
| Individual / Sole proprietor | `"Individual / Sole Proprietor"` |
| C corporation | `"C Corporation"` |
| S corporation | `"S Corporation"` |
| Partnership | `"Partnership"` |
| Trust / estate | `"Trust / Estate"` |
| LLC (C) | `"LLC (C Corporation)"` |
| LLC (S) | `"LLC (S Corporation)"` |
| LLC (P) | `"LLC (Partnership)"` |

### Find/replace the variable name

After renaming `APEX` to your variable (e.g., `ACME`), use your editor's find-and-replace to update **every reference** in the file:

```
Find:    APEX[
Replace: ACME[
```

There are roughly 15–20 references throughout the file. Replace them all.

---

## Step 4 — Customize Your Brand Colors

Below the constants block, find the color palette:

```python
# Different palette from Finemark so it's visually obvious this is NOT real
TEAL      = HexColor("#0E7C7B")   # primary
ORANGE    = HexColor("#E07A1F")   # accent
GREY      = HexColor("#6B7280")
LIGHT_BG  = HexColor("#F0F4F4")
DIVIDER   = HexColor("#D1D5DB")
DARK_TEXT = HexColor("#1A1A1A")
```

**Replace `TEAL` and `ORANGE` with your brand colors** (rename the variables too if you want — make sure to find/replace throughout the file).

### Picking colors that print well

- **Primary color:** Should be dark enough to read white text on. Avoid pastels.
- **Accent color:** Should pop against the primary. Gold, orange, red, or bright blue work well.
- **Both should be CMYK-printable** if you ever print these. Avoid pure RGB neons.

### Quick color recipes for freight / logistics brands

| Vibe | Primary | Accent |
|------|---------|--------|
| Corporate trust | `#1F3A5F` (navy) | `#B8893B` (gold) |
| Modern tech | `#0E7C7B` (teal) | `#E07A1F` (orange) |
| Bold red | `#991B1B` (deep red) | `#FBBF24` (amber) |
| Forest / earthy | `#1F4E2B` (forest) | `#C9A24A` (mustard) |
| Black + accent | `#111827` (near-black) | `#10B981` (emerald) |

Test your colors with a free tool like [coolors.co](https://coolors.co) or [contrast-ratio.com](https://contrast-ratio.com) to make sure white text on your primary passes WCAG AA.

---

## Step 5 — Update the Logo Wordmark

The header bar uses a typographic wordmark — no image file needed. Find this block in `build_packet.py`:

```python
c.setFillColor(white)
c.setFont("Helvetica-Bold", 16)
c.drawString(0.6*inch, height - 0.60*inch, "APEX TRANSIT")
c.setFillColor(ORANGE)
c.setFont("Helvetica", 9)
c.drawString(2.45*inch, height - 0.60*inch, "LLC")
```

Update both strings:

```python
c.drawString(0.6*inch, height - 0.60*inch, "ACME LOGISTICS")
...
c.drawString(2.85*inch, height - 0.60*inch, "LLC")
```

**Important:** If your company name is longer or shorter than "APEX TRANSIT," you'll need to nudge the second `drawString` x-coordinate (the `2.45*inch` part) so the entity suffix doesn't overlap. Roughly:

- Short name (8–11 chars): `2.0*inch`
- Medium name (12–15 chars): `2.45*inch`
- Long name (16+ chars): `3.1*inch`

Render the PDF, look at the header, adjust if needed.

---

## Step 6 — Remove the TEST/DEMO Watermarks

Since you're shipping the live version, you'll want to strip out the safety banners. In `build_packet.py`, find and **delete** these blocks:

### A. Delete the top warning banner

```python
# ---- TOP DEMO BANNER ----
c.setFillColor(DEMO_BANNER)
c.rect(0, height - 0.30*inch, width, 0.30*inch, fill=1, stroke=0)
c.setFillColor(HexColor("#7C2D12"))
c.setFont("Helvetica-Bold", 10)
c.drawCentredString(width/2, height - 0.21*inch,
    "⚠  TEST / DEMO PACKET — FICTIONAL COMPANY — NOT FOR USE WITH REAL VENDORS  ⚠")
```

### B. Delete the diagonal SAMPLE watermark

```python
# ---- Diagonal SAMPLE watermark across body ----
c.saveState()
c.translate(width/2, height/2)
c.rotate(35)
c.setFillColor(WATERMARK_RED)
c.setFont("Helvetica-Bold", 110)
c.drawCentredString(0, -25, "SAMPLE")
c.setFont("Helvetica-Bold", 30)
c.drawCentredString(0, 60, "TEST / DEMO — NOT REAL")
c.restoreState()
```

### C. Delete the bottom warning banner

```python
# Bottom warning banner
c.setFillColor(DEMO_BANNER)
c.rect(0, 0, width, 0.22*inch, fill=1, stroke=0)
c.setFillColor(HexColor("#7C2D12"))
c.setFont("Helvetica-Bold", 8.5)
c.drawCentredString(width/2, 0.07*inch,
    "DEMO DOCUMENT — All names, EINs, account numbers, and addresses are fictitious")
```

### D. Delete inline `[FAKE]` labels

In the section tables, remove the `[FAKE]` red text:

```python
# Before:
("Federal Tax ID (EIN)",  f"<b>{ACME['ein']}</b>  <font color='#B91C1C'>[FAKE]</font>"),

# After:
("Federal Tax ID (EIN)",  f"<b>{ACME['ein']}</b>"),
```

Same for `routing`, `account`, and `mc_number` rows.

### E. Adjust the top margin

Since the top banner is gone, reduce the top margin so the brand bar sits at the top of the page:

```python
# Before:
topMargin=0.95*inch,

# After:
topMargin=0.72*inch,
```

And update the brand bar y-coordinate:

```python
# Before:
c.rect(0, height - 0.75*inch, width, 0.45*inch, fill=1, stroke=0)

# After:
c.rect(0, height - 0.45*inch, width, 0.45*inch, fill=1, stroke=0)
```

(All references to `0.75` and `0.80` for the brand bar should drop by `0.30` to compensate.)

### F. Update the closing note

The DEMO version has a `[DEMO — fictional Apex Transit LLC]` tag in the closing paragraph. Remove it:

```python
# Before:
"earn your business.  "
"<font color='#B91C1C'><b>[DEMO — fictional Apex Transit LLC]</b></font>",

# After:
"earn your business.",
```

### G. Remove "(FICTIONAL)" labels

Search for `(FICTIONAL)` and `(DEMO)` and remove those decorations from the prepared-by block, signature, and section headers.

### H. Remove the `[ DEMO ]` from the title

```python
# Before:
story.append(Paragraph("Vendor Setup Packet  <font size='12' color='#E07A1F'>[ DEMO ]</font>", doc_title))
story.append(Paragraph("Sample W-9 &amp; Remittance Information — TEST / DEMO MODE", sub_title))

# After:
story.append(Paragraph("Vendor Setup Packet", doc_title))
story.append(Paragraph("W-9 &amp; Remittance Information for New Vendor Onboarding", sub_title))
```

---

## Step 7 — Replace the Sample W-9

The demo ships with an auto-generated `sample_w9.pdf`. Replace it with your real signed W-9.

```bash
# Delete the auto-generated sample
rm assets/sample_w9.pdf

# Drop your real signed W-9 into assets/ — and rename it to signed_w9.pdf
cp /path/to/your_signed_w9.pdf assets/signed_w9.pdf
```

Then update the script to point at the new filename. Find:

```python
default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_w9.pdf")
```

Change to:

```python
default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "signed_w9.pdf")
```

Also remove the `build_sample_w9()` function entirely (about 80 lines, the whole function from `def build_sample_w9(path):` down to its `c.save()`) — you won't need it anymore since you're using a real signed PDF.

And remove the auto-generation logic at the top of `main()`:

```python
# Delete this block — you're using a real W-9, not generating one
if not os.path.exists(args.w9_path):
    os.makedirs(os.path.dirname(args.w9_path), exist_ok=True)
    build_sample_w9(args.w9_path)
```

---

## Step 8 — Update the Output Filename

Find this line in `main()`:

```python
final_path = os.path.join(
    args.output_dir, f"ApexTransit_Vendor_Setup_DEMO_{safe_tag}.pdf"
)
```

Change to your company:

```python
final_path = os.path.join(
    args.output_dir, f"AcmeLogistics_Vendor_Setup_{safe_tag}.pdf"
)
```

(Note: drop the `_DEMO_` infix.)

---

## Step 9 — Test It

Run the script with default args and check the output:

```bash
cd your-vendor-setup
python assets/build_packet.py --output-name "TEST"
```

You should see:

```
OK: /mnt/user-data/outputs/AcmeLogistics_Vendor_Setup_TEST.pdf  (2 pages)
```

Open the PDF and verify:

- [ ] Header shows YOUR company name in YOUR primary color
- [ ] No `[FAKE]` labels
- [ ] No SAMPLE watermark
- [ ] No top/bottom yellow warning banners
- [ ] Banking section shows YOUR routing + account
- [ ] EIN matches YOUR W-9
- [ ] Page 2 is YOUR signed W-9, not a generated sample
- [ ] Filename starts with YOUR company name

If anything looks off, check the corresponding step above.

---

## Step 10 — Install

Once it's working, install the skill so it's available in every conversation:

1. Zip the folder:
   ```bash
   zip -r yourcompany-vendor-setup.skill yourcompany-vendor-setup/
   ```
2. Upload the `.skill` file via your Claude settings → Skills → Add custom skill
3. Or drop the unzipped folder into `/mnt/skills/user/` if your environment supports direct file install

Test the trigger by typing one of your trigger phrases:

> "AP wants my W9 and banking — send to faye@example.com"

The skill should fire automatically and produce a packet. If it doesn't fire, check Step 2 (description / trigger phrases).

---

## Common Gotchas

| Problem | Fix |
|---------|-----|
| `field 'description' must be at most 1024 characters` | Trim duplicate trigger phrases in Step 2 |
| Output PDF is 3 pages instead of 2 | Signature spilled — reduce padding in `make_kv_table` |
| Header text overlaps the company name | Adjust the entity suffix x-coordinate in Step 5 |
| Skill doesn't fire on your trigger phrases | Make sure your description in Step 2 includes EXACT phrases you'd actually type |
| W-9 page looks distorted | Make sure your signed W-9 is letter-size (8.5" x 11"), not A4 |
| Colors look washed out when printed | Avoid pastel primary colors — go darker than you think |
| `signed_w9.pdf not found` | Step 7 — make sure the file is in `assets/` and the script's default path matches |

---

## Customization Levels

You don't have to do all 10 steps. Pick your level:

### Quick (5 minutes) — Just my info, keep the demo branding
Steps 3, 7, 8 only. You'll have a working packet with your real info but Apex's teal/orange colors.

### Standard (20 minutes) — My info + my brand
All steps except Step 6 (keep the watermarks for now if you're not ready to ship). Run as a "draft" mode while you finalize.

### Full ship (30 minutes) — Production-ready
All 10 steps. Watermarks gone, real W-9 attached, fully branded, installed and triggering on your phrases.

---

## What You End Up With

After customization, you have a **personal automation that lives in Claude forever**. Every time a customer's AP team asks for your W-9 + banking, you type a sentence and a branded packet appears.

Estimated time savings per packet: **12–15 minutes**.

If you handle even 4 vendor setups a month, this skill pays for itself in saved time the first week.

---

## Want Help?

- Skool community: [skool.com/la-crown-ai-8246](https://skool.com/la-crown-ai-8246)
- Email: millisa@lacrown.ai
- Watch the build video on YouTube: [@lacrown_ai](https://youtube.com/@lacrown_ai)

---

*Template by Millisa Nwokolo · La Crown Inc. · Built on Claude Skills · [lacrown.ai](https://lacrown.ai)*
