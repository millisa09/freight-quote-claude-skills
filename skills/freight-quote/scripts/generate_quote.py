#!/usr/bin/env python3
"""
Freight Quote PDF Generator — config-driven, public version
Part of freight-quote-claude-skills by La Crown Inc. (lacrown.ai)

Usage:
  python generate_quote.py '<json_payload>' [path/to/config.json]

If config path is omitted, looks for config.json in the script's directory.
Outputs the PDF file path on stdout.
"""

import sys, json, re, os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


def hex_to_color(hex_str):
    """Convert #RRGGBB hex string to ReportLab Color."""
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    return colors.Color(r, g, b)


def load_config(config_path=None):
    """Load broker config. Falls back to defaults if config missing."""
    defaults = {
        "broker_company":      "Your Brokerage LLC",
        "broker_mc":           "MC #000000",
        "broker_address":      "Your Address, City, ST 00000",
        "broker_email":        "you@yourbrokerage.com",
        "broker_phone_office": "555-000-0000",
        "broker_phone_mobile": "555-000-0001",
        "broker_contact_name": "Your Name",
        "brand_color_navy":    "#0D2D5E",
        "brand_color_gold":    "#C8A84B",
        "quote_prefix":        "FQ",
        "default_valid_days":  14,
    }
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            user_cfg = json.load(f)
            # strip meta key if present
            user_cfg.pop("_instructions", None)
            defaults.update(user_cfg)
    else:
        # look next to this script
        local = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        if os.path.exists(local):
            with open(local) as f:
                user_cfg = json.load(f)
                user_cfg.pop("_instructions", None)
                defaults.update(user_cfg)
    return defaults


# ── Page geometry ──────────────────────────────────────────────────────────────
LM, RM, TM, BM = 0.7*inch, 0.7*inch, 0.6*inch, 0.65*inch
W = letter[0] - LM - RM

DGRAY = colors.Color(0.333, 0.333, 0.333)
MGRAY = colors.Color(0.467, 0.467, 0.467)
DTXT  = colors.Color(0.2,   0.2,   0.2)
GRID  = colors.Color(0.78,  0.78,  0.78)
LGBG  = colors.Color(0.95,  0.95,  0.95)
WHITE = colors.white
BLACK = colors.black

def S(n, **k): return ParagraphStyle(n, **k)


def build_styles(NAVY, GOLD):
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
    }


def section_hd(text, st, story):
    story.append(Paragraph(text, st["sec_hd"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRID, spaceAfter=5))


def generate(data: dict, cfg: dict) -> str:
    NAVY = hex_to_color(cfg["brand_color_navy"])
    GOLD = hex_to_color(cfg["brand_color_gold"])
    st   = build_styles(NAVY, GOLD)

    today      = datetime.today()
    valid_days = data.get("valid_days", cfg.get("default_valid_days", 14))
    valid_thru = today + timedelta(days=valid_days)
    prefix     = cfg.get("quote_prefix", "FQ")
    quote_num  = data.get("quote_num") or f"{prefix}-{today.strftime('%Y-%m%d')}"

    qt   = data.get("quoted_to", {})
    ship = data.get("shipment",  {})
    items= data.get("line_items", [])
    extra_terms = data.get("extra_terms", [])

    cust_slug = re.sub(r"[^A-Za-z0-9]", "", qt.get("company", "Customer"))
    svc_slug  = re.sub(r"[^A-Za-z0-9]", "", ship.get("service_type", "Quote").split()[0])
    output    = f"/mnt/user-data/outputs/FreightQuote_{cust_slug}_{svc_slug}.pdf"

    doc = SimpleDocTemplate(output, pagesize=letter,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    co_line2 = f"{cfg['broker_mc']} | Freight Brokerage"
    co_line3 = cfg["broker_address"]
    co_line4 = f"Office: {cfg['broker_phone_office']} | {cfg['broker_email']}"

    left_data = [
        [Paragraph(cfg["broker_company"], st["co_name"])],
        [Paragraph(co_line2, st["co_sub"])],
        [Paragraph(co_line3, st["co_sub"])],
        [Paragraph(co_line4, st["co_sub"])],
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
    fields = [
        ("contact",        "Contact:"),
        ("address",        "Address:"),
        ("phone",          "Phone:"),
        ("seller_name",    "Requested By:"),
        ("seller_company", "Seller:"),
        ("seller_email",   "Email:"),
        ("seller_phone",   "Phone:"),
    ]
    for key, label in fields:
        if qt.get(key):
            qt_rows.append([Paragraph(label, st["lbl_key"]),
                            Paragraph(qt[key], st["lbl_val"])])
    qt_tbl = Table(qt_rows, colWidths=[1.2*inch, W - 1.2*inch])
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
    H, LW2 = W/2, 1.05*inch
    VW2 = H - LW2
    def sr(l1, v1, l2, v2):
        return [Paragraph(l1, st["lbl_key"]), Paragraph(v1, st["lbl_val"]),
                Paragraph(l2, st["lbl_key"]), Paragraph(v2, st["lbl_val"])]
    sd_rows = [
        sr("Origin:",      ship.get("origin",""),      "Destination:",  ship.get("destination","")),
        sr("Est. Miles:",  ship.get("est_miles",""),   "Service Type:", ship.get("service_type","")),
        sr("Commodity:",   ship.get("commodity",""),   "Equipment:",    ship.get("equipment","")),
        sr("Weight:",      ship.get("weight",""),      "Permit Class:", ship.get("permit_class","")),
        sr("Dimensions:",  ship.get("dimensions",""),  "Est. Transit:", ship.get("est_transit","")),
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
    pr_rows = [[Paragraph(i.get("description",""), st["pr_val"]),
                Paragraph(i.get("notes",""),        st["pr_val"]),
                Paragraph(i.get("amount",""),        st["pr_valr"])] for i in items]
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
        Paragraph(data.get("total_label","TOTAL FLAT RATE"), st["tot_lbl"]),
        Paragraph(data.get("total_note","All-inclusive | No hidden fees"), st["tot_mid"]),
        Paragraph(data.get("total_amount",""), st["tot_amt"]),
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
    contact = cfg.get("broker_contact_name", "Your Broker")
    standard_terms = [
        "Payment is due in full prior to scheduling pickup. No shipment will be tendered until payment is confirmed.",
        f"This quote is valid for {valid_days} days from the issue date ({today.strftime('%B %d, %Y')} through {valid_thru.strftime('%B %d, %Y')}).",
        "Rate applies to the service type noted above. No inside delivery, liftgate, or residential surcharges are included unless specified.",
        "Shipper is responsible for proper blocking, bracing, and securing of freight prior to pickup.",
        "Any dimensional or weight discrepancies at time of pickup may result in a rate adjustment.",
        "Detention, driver-assist, or re-consignment charges are not included and will be billed separately if incurred.",
        f"{cfg['broker_company']} operates as a licensed freight broker ({cfg['broker_mc']}). Carrier selection at our discretion.",
        "<b>Cargo Insurance:</b> The carrier selected for this shipment will carry a minimum of $100,000 in cargo insurance. "
            "Any cargo value exceeding $100,000 must be disclosed prior to booking. Shipper is responsible for obtaining a "
            "shipper's interest insurance policy to cover any value above the carrier's cargo liability limit.",
    ]
    for i, t in enumerate(standard_terms + (extra_terms or []), 1):
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
        f"Questions? Contact {contact} at {cfg['broker_email']} | {cfg['broker_phone_office']} | M: {cfg['broker_phone_mobile']}",
        st["foot_s"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        f"{cfg['broker_company']}  |  {cfg['broker_mc']}  |  {cfg['broker_address']}",
        st["foot_s"]))

    doc.build(story)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_quote.py '<json>' [config.json]", file=sys.stderr)
        sys.exit(1)
    payload     = json.loads(sys.argv[1])
    config_path = sys.argv[2] if len(sys.argv) > 2 else None
    cfg         = load_config(config_path)
    out         = generate(payload, cfg)
    print(out)
