#!/usr/bin/env python3
"""
generate_quote.py — Generic Freight Quote PDF Generator
Built by La Crown Inc. | lacrown.ai

Usage:
    python generate_quote.py examples/sample_payload.json
    python generate_quote.py '<json string>'

Branding is loaded from config/broker_config.json — update that file once
and every quote reflects your company automatically.

Outputs the PDF path on stdout on success.
"""

import sys
import json
import re
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab", file=sys.stderr)
    sys.exit(1)

# ── Find config and output paths ───────────────────────────────────────────────
SKILL_ROOT = Path(__file__).parent.parent
CONFIG_PATH = SKILL_ROOT / "config" / "broker_config.json"
OUTPUT_DIR  = Path(os.environ.get("QUOTE_OUTPUT_DIR", "/mnt/user-data/outputs"))

# ── Load broker config ─────────────────────────────────────────────────────────
def load_config() -> dict:
    defaults = {
        "company_name":   "YOUR BROKERAGE NAME",
        "mc_number":      "MC #000000",
        "address":        "Your Address, City, ST ZIP",
        "phone":          "000-000-0000",
        "mobile":         "",
        "email":          "you@yourdomain.com",
        "brand_navy":     "#003366",
        "brand_gold":     "#C8961E",
        "valid_days":     14,
        "linehaul_floor": 2.50,
        "cargo_insurance_clause": (
            "The carrier selected for this shipment will carry a minimum of $100,000 "
            "in cargo insurance. Any cargo value exceeding $100,000 must be disclosed "
            "prior to booking. Shipper is responsible for obtaining a shipper's interest "
            "insurance policy to cover any value above the carrier's cargo liability limit."
        )
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user_cfg = json.load(f)
            defaults.update(user_cfg)
        except Exception:
            pass
    return defaults


def hex_to_color(h: str):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return colors.Color(r/255, g/255, b/255)


# ── Style factory ──────────────────────────────────────────────────────────────
def build_styles(cfg: dict) -> dict:
    NAVY  = hex_to_color(cfg["brand_navy"])
    GOLD  = hex_to_color(cfg["brand_gold"])
    DGRAY = colors.Color(0.333, 0.333, 0.333)
    MGRAY = colors.Color(0.467, 0.467, 0.467)
    DTXT  = colors.Color(0.2,   0.2,   0.2)
    BLACK = colors.black

    def S(n, **k): return ParagraphStyle(n, **k)

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
        "_navy":    NAVY,
        "_gold":    GOLD,
        "_grid":    colors.Color(0.78, 0.78, 0.78),
        "_lgbg":    colors.Color(0.95, 0.95, 0.95),
    }


def section_hd(text, st, story):
    story.append(Paragraph(text, st["sec_hd"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=st["_grid"], spaceAfter=5))


# ── Main PDF generator ─────────────────────────────────────────────────────────
def generate(data: dict, cfg: dict) -> str:
    st   = build_styles(cfg)
    NAVY = st["_navy"]
    GOLD = st["_gold"]
    GRID = st["_grid"]
    LGBG = st["_lgbg"]
    WHITE = colors.white

    today      = datetime.today()
    valid_days = data.get("valid_days", cfg.get("valid_days", 14))
    valid_thru = today + timedelta(days=valid_days)

    # Auto-generate quote number if not provided
    quote_num = data.get("quote_num")
    if not quote_num or quote_num == "auto":
        prefix = re.sub(r"[^A-Z0-9]", "", cfg["company_name"].upper())[:3] or "FRQ"
        quote_num = f"{prefix}-{today.strftime('%Y-%m%d')}"

    qt   = data.get("quoted_to", {})
    ship = data.get("shipment",  {})
    items= data.get("line_items", [])
    extra_terms = data.get("extra_terms", [])

    # Output filename
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cust_slug = re.sub(r"[^A-Za-z0-9]", "", qt.get("company", "Customer"))
    svc_slug  = re.sub(r"[^A-Za-z0-9]", "", ship.get("service_type", "Quote").split()[0])
    co_slug   = re.sub(r"[^A-Za-z0-9]", "", cfg["company_name"])
    output    = str(OUTPUT_DIR / f"{co_slug}_Quote_{cust_slug}_{svc_slug}.pdf")

    LM, RM, TM, BM = 0.7*inch, 0.7*inch, 0.6*inch, 0.65*inch
    W = letter[0] - LM - RM

    doc = SimpleDocTemplate(output, pagesize=letter,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    mc_line = f"{cfg['mc_number']} | Freight Brokerage" if cfg.get("mc_number") else "Freight Brokerage"
    mobile_line = f"Office: {cfg['phone']}" + (f" | Mobile: {cfg['mobile']}" if cfg.get("mobile") else "")

    left_data = [
        [Paragraph(cfg["company_name"].upper(), st["co_name"])],
        [Paragraph(mc_line, st["co_sub"])],
        [Paragraph(cfg["address"], st["co_sub"])],
        [Paragraph(f"{mobile_line} | {cfg['email']}", st["co_sub"])],
    ]
    left_tbl = Table(left_data, colWidths=[4.1*inch])
    left_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    LBL_W, VAL_W = 0.9*inch, 2.0*inch
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
    for lbl, key in [("Contact:", "contact"), ("Requested By:", "seller_name"),
                     ("Seller:", "seller_company"), ("Email:", "seller_email"),
                     ("Phone:", "seller_phone")]:
        if qt.get(key):
            qt_rows.append([Paragraph(lbl, st["lbl_key"]), Paragraph(qt[key], st["lbl_val"])])
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
    H, LW2 = W / 2, 1.05*inch
    VW2 = H - LW2

    def ship_row(l1, v1, l2, v2):
        return [Paragraph(l1, st["lbl_key"]), Paragraph(v1, st["lbl_val"]),
                Paragraph(l2, st["lbl_key"]), Paragraph(v2, st["lbl_val"])]

    sd_rows = [
        ship_row("Origin:",     ship.get("origin",""),      "Destination:",  ship.get("destination","")),
        ship_row("Est. Miles:", ship.get("est_miles",""),   "Service Type:", ship.get("service_type","")),
        ship_row("Commodity:",  ship.get("commodity",""),   "Equipment:",    ship.get("equipment","")),
        ship_row("Weight:",     ship.get("weight",""),      "Permit Class:", ship.get("permit_class","Standard")),
        ship_row("Dimensions:", ship.get("dimensions",""),  "Est. Transit:", ship.get("est_transit","")),
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
    C1, C3 = 2.0*inch, 1.0*inch
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

    tot = Table([[
        Paragraph(data.get("total_label","TOTAL FLAT RATE"),          st["tot_lbl"]),
        Paragraph(data.get("total_note","All-inclusive | No hidden fees"), st["tot_mid"]),
        Paragraph(data.get("total_amount",""),                        st["tot_amt"]),
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
        "Rate applies to the service type noted above. No inside delivery, liftgate, or residential surcharges "
            "are included unless specified in the Pricing Summary.",
        "Shipper is responsible for proper blocking, bracing, and securing of freight prior to pickup.",
        "Any dimensional or weight discrepancies at time of pickup may result in a rate adjustment.",
        "Detention, driver-assist, layover, or re-consignment charges are not included and will be billed "
            "separately if incurred.",
        f"{cfg['company_name']} operates as a licensed freight broker ({cfg['mc_number']}). "
            "Carrier selection at our discretion.",
        f"<b>Cargo Insurance:</b> {cfg['cargo_insurance_clause']}",
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
    SL = 2.4*inch
    sig = Table([
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
    contact_parts = [f"{cfg['email']}", f"{cfg['phone']}"]
    if cfg.get("mobile"):
        contact_parts.append(f"M: {cfg['mobile']}")
    story.append(Paragraph(
        f"Thank you for the opportunity to earn your business. Questions? Contact us at {' | '.join(contact_parts)}",
        st["foot_s"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        f"{cfg['company_name']}  |  {cfg['mc_number']}  |  {cfg['address']}",
        st["foot_s"]))

    doc.build(story)
    return output


def load_payload(arg: str) -> dict:
    """Load JSON payload from file path or inline JSON string."""
    arg = arg.strip()
    if arg.startswith("{"):
        return json.loads(arg)
    path = Path(arg)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    raise ValueError(f"Cannot load payload: {arg}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_quote.py <payload.json | '{...}'>", file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    payload = load_payload(sys.argv[1])
    out = generate(payload, cfg)
    print(out)
