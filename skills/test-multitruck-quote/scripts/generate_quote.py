#!/usr/bin/env python3
"""
Apex Transit LLC — Multi-Truck Heavy Haul Quote PDF Generator (TEST/DEMO VERSION)
Usage: python generate_quote.py '<json_payload>'
Outputs the PDF path on stdout on success.

NOTE: This is a sandbox/demo skill using fictional brokerage info.
Do NOT use for real customer-facing quotes.
Built for social media demos, YouTube recordings, and skill development.
"""

import sys, json, re
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Brand colors ───────────────────────────────────────────────────────────────
NAVY  = colors.Color(0.0,  0.2,  0.4)
GOLD  = colors.Color(0.784,0.588,0.047)
DGRAY = colors.Color(0.333,0.333,0.333)
MGRAY = colors.Color(0.467,0.467,0.467)
DTXT  = colors.Color(0.2,  0.2,  0.2)
GRID  = colors.Color(0.78, 0.78, 0.78)
LGBG  = colors.Color(0.95, 0.95, 0.95)
WHITE = colors.white
BLACK = colors.black

# ── Fake Brokerage Info (TEST ONLY) ───────────────────────────────────────────
BROKERAGE_NAME    = "APEX TRANSIT LLC"
BROKERAGE_MC      = "MC #123456"
BROKERAGE_ADDRESS = "PO Box 4400, Indianapolis, IN 46201"
BROKERAGE_PHONE   = "317-555-0192"
BROKERAGE_EMAIL   = "quotes@apextransit.com"
BROKERAGE_CONTACT = "Alex Rivera"
BROKERAGE_MOBILE  = "317-555-0847"
QUOTE_PREFIX      = "ATQ"   # Apex Transit Quote

# ── Page geometry ──────────────────────────────────────────────────────────────
LM, RM, TM, BM = 0.7*inch, 0.7*inch, 0.6*inch, 0.65*inch
W = letter[0] - LM - RM   # 7.1"

# ── Style factory ──────────────────────────────────────────────────────────────
def S(n, **k): return ParagraphStyle(n, **k)

def build_styles():
    return {
        "co_name":  S("CN",  fontSize=20, fontName="Helvetica-Bold", textColor=NAVY,  leading=24),
        "co_sub":   S("CS",  fontSize=10, fontName="Helvetica",      textColor=DGRAY, leading=15),
        "fq_big":   S("FB",  fontSize=20, fontName="Helvetica-Bold", textColor=GOLD,  leading=24, alignment=TA_RIGHT),
        "meta_lbl": S("ML",  fontSize=9,  fontName="Helvetica-Bold", textColor=DTXT,  leading=13, alignment=TA_RIGHT),
        "meta_val": S("MV",  fontSize=9,  fontName="Helvetica",      textColor=DTXT,  leading=13),
        "sec_hd":   S("SH",  fontSize=11, fontName="Helvetica-Bold", textColor=NAVY,  leading=16),
        "lbl_key":  S("LK",  fontSize=9,  fontName="Helvetica-Bold", textColor=MGRAY, leading=13),
        "lbl_val":  S("LV",  fontSize=10, fontName="Helvetica",      textColor=BLACK, leading=14),
        "lbl_valb": S("LVB", fontSize=10, fontName="Helvetica-Bold", textColor=BLACK, leading=14),
        "pr_hd":    S("PH",  fontSize=9,  fontName="Helvetica-Bold", textColor=DTXT,  leading=13),
        "pr_hdr":   S("PHR", fontSize=9,  fontName="Helvetica-Bold", textColor=DTXT,  leading=13, alignment=TA_RIGHT),
        "pr_val":   S("PV",  fontSize=9,  fontName="Helvetica",      textColor=DTXT,  leading=13),
        "pr_valr":  S("PVR", fontSize=9,  fontName="Helvetica",      textColor=DTXT,  leading=13, alignment=TA_RIGHT),
        "tot_lbl":  S("TL",  fontSize=10, fontName="Helvetica-Bold", textColor=DTXT,  leading=14),
        "tot_mid":  S("TM",  fontSize=9,  fontName="Helvetica-Oblique", textColor=MGRAY, leading=13),
        "tot_amt":  S("TA",  fontSize=12, fontName="Helvetica-Bold", textColor=GOLD,  leading=16, alignment=TA_RIGHT),
        "terms_s":  S("TS",  fontSize=9,  fontName="Helvetica",      textColor=DTXT,  leading=13),
        "accept_s": S("AS",  fontSize=10, fontName="Helvetica",      textColor=BLACK, leading=14),
        "foot_s":   S("FS",  fontSize=8,  fontName="Helvetica",      textColor=MGRAY, leading=11, alignment=TA_CENTER),
        "demo_tag": S("DT",  fontSize=7,  fontName="Helvetica-Oblique", textColor=colors.Color(0.6,0.3,0.3), leading=10, alignment=TA_CENTER),
    }

# ── Section header: navy bold + thin gray rule ─────────────────────────────────
def section_hd(text, st, story):
    story.append(Paragraph(text, st["sec_hd"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRID, spaceAfter=5))

# ── Main generator ─────────────────────────────────────────────────────────────
def generate(data: dict) -> str:
    st = build_styles()

    today      = datetime.today()
    valid_days = data.get("valid_days", 14)
    valid_thru = today + timedelta(days=valid_days)
    quote_num  = data.get("quote_num") or f"{QUOTE_PREFIX}-{today.strftime('%Y-%m%d')}"

    qt   = data.get("quoted_to", {})
    ship = data.get("shipment",  {})
    items= data.get("line_items", [])
    extra_terms = data.get("extra_terms", [])

    # Derive customer slug for filename (multi-truck pattern)
    cust_slug = re.sub(r"[^A-Za-z0-9]", "", qt.get("company", "Customer"))
    output    = f"/mnt/user-data/outputs/ApexTransit_MultiTruck_{cust_slug}.pdf"

    doc = SimpleDocTemplate(output, pagesize=letter,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)

    story = []

    # ── DEMO WATERMARK BANNER ─────────────────────────────────────────────────
    story.append(Paragraph("*** TEST / DEMO DOCUMENT — NOT FOR CUSTOMER USE ***", st["demo_tag"]))
    story.append(Spacer(1, 4))

    # ── HEADER ────────────────────────────────────────────────────────────────
    left_data = [
        [Paragraph(BROKERAGE_NAME, st["co_name"])],
        [Paragraph(f"{BROKERAGE_MC} | Freight Brokerage", st["co_sub"])],
        [Paragraph(BROKERAGE_ADDRESS, st["co_sub"])],
        [Paragraph(f"Office: {BROKERAGE_PHONE} | {BROKERAGE_EMAIL}", st["co_sub"])],
    ]
    left_tbl = Table(left_data, colWidths=[4.1*inch])
    left_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    LBL_W = 0.9*inch
    VAL_W = 2.0*inch
    right_data = [
        [Paragraph("FREIGHT QUOTE", st["fq_big"]), ""],
        [Paragraph("Quote #:",     st["meta_lbl"]), Paragraph(quote_num,                        st["meta_val"])],
        [Paragraph("Date:",        st["meta_lbl"]), Paragraph(today.strftime("%B %d, %Y"),      st["meta_val"])],
        [Paragraph("Valid Until:", st["meta_lbl"]), Paragraph(valid_thru.strftime("%B %d, %Y"), st["meta_val"])],
    ]
    right_tbl = Table(right_data, colWidths=[LBL_W, VAL_W])
    right_tbl.setStyle(TableStyle([
        ("SPAN",          (0,0),(1,0)),
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 3),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    RIGHT_W = LBL_W + VAL_W
    hdr = Table([[left_tbl, right_tbl]], colWidths=[W - RIGHT_W, RIGHT_W])
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=10))

    # ── QUOTED TO ─────────────────────────────────────────────────────────────
    section_hd("QUOTED TO:", st, story)

    qt_rows = [[Paragraph(qt.get("company", ""), st["lbl_valb"]), ""]]
    if qt.get("contact"):
        qt_rows.append([Paragraph("Contact:",      st["lbl_key"]), Paragraph(qt["contact"],       st["lbl_val"])])
    if qt.get("seller_name"):
        qt_rows.append([Paragraph("Requested By:", st["lbl_key"]), Paragraph(qt["seller_name"],   st["lbl_val"])])
    if qt.get("seller_company"):
        qt_rows.append([Paragraph("Seller:",       st["lbl_key"]), Paragraph(qt["seller_company"],st["lbl_val"])])
    if qt.get("seller_email"):
        qt_rows.append([Paragraph("Email:",        st["lbl_key"]), Paragraph(qt["seller_email"],  st["lbl_val"])])
    if qt.get("seller_phone"):
        qt_rows.append([Paragraph("Phone:",        st["lbl_key"]), Paragraph(qt["seller_phone"],  st["lbl_val"])])

    qt_tbl = Table(qt_rows, colWidths=[1.15*inch, W - 1.15*inch])
    qt_tbl.setStyle(TableStyle([
        ("SPAN",          (0,0),(1,0)),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    story.append(qt_tbl)
    story.append(Spacer(1, 12))

    # ── SHIPMENT DETAILS ──────────────────────────────────────────────────────
    section_hd("SHIPMENT DETAILS", st, story)

    H   = W / 2
    LW2 = 1.05*inch
    VW2 = H - LW2

    def ship_row(l1, v1, l2, v2):
        return [Paragraph(l1, st["lbl_key"]), Paragraph(v1, st["lbl_val"]),
                Paragraph(l2, st["lbl_key"]), Paragraph(v2, st["lbl_val"])]

    sd_rows = [
        ship_row("Origin:",      ship.get("origin",""),      "Destination:",  ship.get("destination","")),
        ship_row("Est. Miles:",  ship.get("est_miles",""),   "Service Type:", ship.get("service_type","")),
        ship_row("Commodity:",   ship.get("commodity",""),   "Equipment:",    ship.get("equipment","")),
        ship_row("Weight:",      ship.get("weight",""),      "Permit Class:", ship.get("permit_class","")),
        ship_row("Dimensions:",  ship.get("dimensions",""),  "Est. Transit:", ship.get("est_transit","")),
    ]
    sd = Table(sd_rows, colWidths=[LW2, VW2, LW2, VW2])
    sd.setStyle(TableStyle([
        ("GRID",          (0,0),(-1,-1), 0.4, GRID),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LGBG, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(sd)
    story.append(Spacer(1, 12))

    # ── PRICING SUMMARY ───────────────────────────────────────────────────────
    section_hd("PRICING SUMMARY", st, story)

    C1 = 2.0*inch
    C3 = 1.0*inch
    C2 = W - C1 - C3

    hdr_row = Table([[
        Paragraph("Description", st["pr_hd"]),
        Paragraph("Notes",       st["pr_hd"]),
        Paragraph("Amount",      st["pr_hdr"]),
    ]], colWidths=[C1, C2, C3])
    hdr_row.setStyle(TableStyle([
        ("LINEBELOW",     (0,0),(-1,-1), 0.8, NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]))
    story.append(hdr_row)

    pr_rows = []
    for item in items:
        pr_rows.append([
            Paragraph(item.get("description",""), st["pr_val"]),
            Paragraph(item.get("notes",""),       st["pr_val"]),
            Paragraph(item.get("amount",""),      st["pr_valr"]),
        ])

    pr_tbl = Table(pr_rows, colWidths=[C1, C2, C3])
    pr_tbl.setStyle(TableStyle([
        ("GRID",          (0,0),(-1,-1), 0.4, GRID),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LGBG]),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (2,0),(2,-1),  "RIGHT"),
    ]))
    story.append(pr_tbl)

    total_label  = data.get("total_label",  "QUOTED RATES")
    total_note   = data.get("total_note",   "Customer to select Option 1 or Option 2 prior to booking")
    total_amount = data.get("total_amount", "")

    tot = Table([[
        Paragraph(total_label,  st["tot_lbl"]),
        Paragraph(total_note,   st["tot_mid"]),
        Paragraph(total_amount, st["tot_amt"]),
    ]], colWidths=[C1, C2, C3])
    tot.setStyle(TableStyle([
        ("LINEABOVE",     (0,0),(-1,0),  1.2, NAVY),
        ("LINEBELOW",     (0,0),(-1,0),  1.2, NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(tot)
    story.append(Spacer(1, 12))

    # ── TERMS & CONDITIONS ────────────────────────────────────────────────────
    section_hd("TERMS & CONDITIONS", st, story)

    standard_terms = [
        "Payment is due in full prior to scheduling pickup. No shipment will be tendered until payment is confirmed.",
        f"This quote is valid for {valid_days} days from the issue date "
            f"({today.strftime('%B %d, %Y')} through {valid_thru.strftime('%B %d, %Y')}).",
        "Rate applies to the service type noted above. No inside delivery, liftgate, or residential surcharges are included unless specified.",
        "Shipper is responsible for proper blocking, bracing, and securing of freight prior to pickup.",
        "Any dimensional or weight discrepancies at time of pickup may result in a rate adjustment.",
        "Detention, driver-assist, or re-consignment charges are not included and will be billed separately if incurred.",
        f"{BROKERAGE_NAME} operates as a licensed freight broker ({BROKERAGE_MC}). Carrier selection at our discretion.",
        "<b>Cargo Insurance:</b> The carrier selected for this shipment will carry a minimum of $100,000 in cargo "
            "insurance. Any cargo value exceeding $100,000 must be disclosed prior to booking. Shipper is "
            "responsible for obtaining a shipper's interest insurance policy to cover any value above the "
            "carrier's cargo liability limit.",
    ]

    all_terms = standard_terms + (extra_terms or [])
    for i, t in enumerate(all_terms, 1):
        story.append(Paragraph(f"{i}. {t}", st["terms_s"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 14))

    # ── ACCEPTANCE ────────────────────────────────────────────────────────────
    section_hd("ACCEPTANCE", st, story)
    story.append(Spacer(1, 8))

    LINE = colors.Color(0.6, 0.6, 0.6)
    SL   = 2.4*inch
    sig  = Table([
        [Paragraph("Authorized Signature:", st["accept_s"]), "", Paragraph("Date:",  st["accept_s"]), ""],
        [Paragraph("Printed Name:",         st["accept_s"]), "", Paragraph("Title:", st["accept_s"]), ""],
    ], colWidths=[1.3*inch, SL, 0.55*inch, SL - 0.25*inch])
    sig.setStyle(TableStyle([
        ("LINEBELOW",     (1,0),(1,0), 0.5, LINE),
        ("LINEBELOW",     (3,0),(3,0), 0.5, LINE),
        ("LINEBELOW",     (1,1),(1,1), 0.5, LINE),
        ("LINEBELOW",     (3,1),(3,1), 0.5, LINE),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("VALIGN",        (0,0),(-1,-1), "BOTTOM"),
    ]))
    story.append(sig)
    story.append(Spacer(1, 20))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRID, spaceAfter=5))
    story.append(Paragraph(
        f"Thank you for the opportunity to earn your business. "
        f"Questions? Contact {BROKERAGE_CONTACT} at {BROKERAGE_EMAIL} | {BROKERAGE_PHONE} | M: {BROKERAGE_MOBILE}",
        st["foot_s"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        f"{BROKERAGE_NAME}  |  {BROKERAGE_MC}  |  {BROKERAGE_ADDRESS}",
        st["foot_s"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("*** TEST DOCUMENT — FICTIONAL BROKERAGE — DO NOT DISTRIBUTE ***", st["demo_tag"]))

    doc.build(story)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_quote.py '<json>'", file=sys.stderr)
        sys.exit(1)
    payload = json.loads(sys.argv[1])
    out = generate(payload)
    print(out)
