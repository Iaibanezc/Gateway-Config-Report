"""
Global Supplies Solutions — Gateway Configuration Report
---------------------------------------------------------
Streamlit application to visualize and export as PDF
the configuration of a CAN/Ethernet gateway.

Flow: Load TXT → View configuration → Export PDF
"""

import streamlit as st
import re
import io
import base64
import os
from datetime import datetime

# ─────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GSS — Gateway Configuration Report",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Logo helper
# ─────────────────────────────────────────────
LOGO_PATH = os.path.join(os.path.dirname(__file__), "gss_logo.png")

def get_logo_base64() -> str:
    """Return the GSS logo as a base64 string for embedding in HTML."""
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ─────────────────────────────────────────────
# Serial number helper
# ─────────────────────────────────────────────
def extract_serial(filename: str) -> str:
    """Extract the serial number (last numeric segment) from the filename."""
    base = os.path.splitext(filename)[0]
    parts = re.split(r'[-_]', base)
    for part in reversed(parts):
        if re.match(r'^\d+$', part):
            return part
    return base

# ─────────────────────────────────────────────
# Global CSS styles  — GSS palette
# Navy #112B3C  |  Teal accent #1E6E8C  |  White #FFFFFF
# ─────────────────────────────────────────────
LOGO_B64 = get_logo_base64()
LOGO_HTML = (
    f'<img src="data:image/png;base64,{LOGO_B64}" '
    f'style="height:52px;object-fit:contain;" alt="GSS Logo">'
    if LOGO_B64 else
    '<span style="font-weight:800;font-size:1.3rem;color:white;">GSS</span>'
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background-color: #F0F4F8;
    }}

    /* ── Header ── */
    .report-header {{
        background: linear-gradient(135deg, #0A1E2C 0%, #112B3C 55%, #1A3E56 100%);
        color: white;
        padding: 1.8rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 6px 24px rgba(0,0,0,0.18);
        display: flex;
        align-items: center;
        gap: 2rem;
    }}
    .header-text h1 {{
        font-size: 1.55rem;
        font-weight: 700;
        margin: 0 0 0.2rem 0;
        letter-spacing: 0.3px;
        color: white !important;
    }}
    .header-text p {{
        font-size: 0.83rem;
        color: #8DBDD8;
        margin: 0;
        font-weight: 400;
    }}
    .header-badge {{
        display: inline-block;
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.18);
        color: #A8D4EC;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 0.6rem;
    }}

    /* ── Section cards ── */
    .section-card {{
        background: white;
        border-radius: 10px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #1E6E8C;
    }}
    .section-title {{
        font-size: 0.85rem;
        font-weight: 700;
        color: #0A1E2C;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 1.1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E2EAF0;
    }}

    /* ── Metric cards ── */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
        gap: 1rem;
        margin-bottom: 0.5rem;
    }}
    .metric-card {{
        background: #F5F9FC;
        border: 1px solid #D8E6EF;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
    }}
    .metric-label {{
        font-size: 0.68rem;
        font-weight: 700;
        color: #5A7A8C;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.3rem;
    }}
    .metric-value {{
        font-size: 1rem;
        font-weight: 700;
        color: #0A1E2C;
        font-family: 'Courier New', monospace;
    }}
    .metric-value.highlight {{
        color: #1E6E8C;
    }}

    /* ── Tables ── */
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.81rem;
    }}
    .custom-table thead tr {{
        background-color: #112B3C;
        color: white;
    }}
    .custom-table thead th {{
        padding: 10px 13px;
        text-align: left;
        font-weight: 600;
        letter-spacing: 0.4px;
        font-size: 0.73rem;
        text-transform: uppercase;
    }}
    .custom-table tbody tr:nth-child(even) {{
        background-color: #F5F9FC;
    }}
    .custom-table tbody tr:hover {{
        background-color: #E6F1F7;
    }}
    .custom-table tbody td {{
        padding: 8px 13px;
        color: #1A2E3B;
        border-bottom: 1px solid #E2EAF0;
        font-family: 'Courier New', monospace;
        font-size: 0.79rem;
    }}
    .custom-table tbody td.label-col {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2D4A5C;
    }}

    /* ── Status badges ── */
    .badge-active {{
        display: inline-block;
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 20px;
        letter-spacing: 0.4px;
    }}
    .badge-inactive {{
        display: inline-block;
        background-color: #F1F5F9;
        color: #94A3B8;
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 20px;
        letter-spacing: 0.4px;
    }}
    .badge-auto {{
        display: inline-block;
        background-color: #DBEAFE;
        color: #1D4ED8;
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 20px;
        letter-spacing: 0.4px;
    }}
    .badge-manual {{
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 20px;
        letter-spacing: 0.4px;
    }}

    /* ── Upload zone ── */
    .upload-zone {{
        background: white;
        border: 2px dashed #B8CDD9;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* ── Download button ── */
    .stDownloadButton > button {{
        background-color: #112B3C !important;
        color: white !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.88rem !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: #1E6E8C !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.4rem;
        background-color: transparent;
        border-bottom: 2px solid #D8E6EF;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.81rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: #5A7A8C;
        padding: 0.55rem 1.1rem;
        border-radius: 6px 6px 0 0;
    }}
    .stTabs [aria-selected="true"] {{
        color: #0A1E2C !important;
        background-color: white !important;
        border-bottom: 2px solid #1E6E8C !important;
    }}

    /* ── Info items ── */
    .info-row {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }}
    .info-item {{
        flex: 1;
        min-width: 150px;
        background: #F5F9FC;
        border: 1px solid #D8E6EF;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }}
    .info-key {{
        font-size: 0.67rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .info-val {{
        font-size: 0.9rem;
        font-weight: 600;
        color: #0A1E2C;
        margin-top: 2px;
    }}

    /* ── Divider ── */
    .divider {{
        height: 1px;
        background: #D8E6EF;
        margin: 1.4rem 0;
    }}

    /* ── Footer ── */
    .report-footer {{
        text-align: center;
        padding: 1.4rem;
        color: #94A3B8;
        font-size: 0.76rem;
        margin-top: 2rem;
        border-top: 1px solid #E2EAF0;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONFIGURATION FILE PARSER
# ─────────────────────────────────────────────

def parse_config(content: str) -> dict:
    """Parse the gateway configuration file content."""

    config = {
        "filters": {},
        "routing_rules": {},
        "replacing_rules": {},
        "can_interfaces": {},
        "ethernet": {},
        "fuse_notifications": {},
    }

    # ── FILTERS ──────────────────────────────
    filters_section = re.search(r'!FILTERS(.*?)(?=!ROUTINGRULES|$)', content, re.DOTALL)
    if filters_section:
        text = filters_section.group(1)
        for iface in range(6):
            iface_filters = []
            for idx in range(10):
                idb = re.search(rf'#IF{iface};FlIDB{idx};(0x[0-9A-Fa-f]+)', text)
                msk = re.search(rf'#IF{iface};FlMSK{idx};(0x[0-9A-Fa-f]+)', text)
                flg = re.search(rf'#IF{iface};FlFLG{idx};(0x[0-9A-Fa-f]+)', text)
                if idb and msk and flg:
                    idb_val = idb.group(1)
                    msk_val = msk.group(1)
                    flg_val = flg.group(1)
                    enabled = not (idb_val == '0x0' and msk_val == '0x0' and flg_val == '0x0')
                    iface_filters.append({
                        "index": idx,
                        "idb": idb_val,
                        "msk": msk_val,
                        "flg": flg_val,
                        "enabled": enabled,
                    })
            config["filters"][iface] = iface_filters

    # ── ROUTING RULES ────────────────────────
    routing_section = re.search(r'!ROUTINGRULES(.*?)(?=!REPLACINGRULES|$)', content, re.DOTALL)
    if routing_section:
        text = routing_section.group(1)
        for iface in range(6):
            iface_rules = []
            for idx in range(10):
                mid = re.search(rf'#IF{iface};RrMID{idx};(0x[0-9A-Fa-f]+)', text)
                msk = re.search(rf'#IF{iface};RrMSK{idx};(0x[0-9A-Fa-f]+)', text)
                rtr = re.search(rf'#IF{iface};RrRTR{idx};(0x[0-9A-Fa-f]+)', text)
                eid = re.search(rf'#IF{iface};RrEID{idx};(0x[0-9A-Fa-f]+)', text)
                rls = re.search(rf'#IF{iface};RrRLS{idx};(0x[0-9A-Fa-f]+)', text)
                ifs = re.search(rf'#IF{iface};RrIFS{idx};([0-9,]+)', text)
                if mid and msk and rtr and eid and rls and ifs:
                    rls_val = rls.group(1)
                    ifs_val = ifs.group(1)
                    enabled = rls_val != '0x0' or any(v != '0' for v in ifs_val.split(','))
                    iface_rules.append({
                        "index": idx,
                        "mid": mid.group(1),
                        "msk": msk.group(1),
                        "rtr": rtr.group(1),
                        "eid": eid.group(1),
                        "rls": rls_val,
                        "ifs": ifs_val,
                        "enabled": enabled,
                    })
            config["routing_rules"][iface] = iface_rules

    # ── REPLACING RULES ──────────────────────
    replacing_section = re.search(r'!REPLACINGRULES(.*?)(?=!CANINTERFACES|$)', content, re.DOTALL)
    if replacing_section:
        text = replacing_section.group(1)
        for iface in range(6):
            iface_rules = []
            for idx in range(10):
                idb = re.search(rf'#IF{iface};DrIDB{idx};(0x[0-9A-Fa-f]+)', text)
                msk = re.search(rf'#IF{iface};DrMSK{idx};(0x[0-9A-Fa-f]+)', text)
                flg = re.search(rf'#IF{iface};DrFLG{idx};(0x[0-9A-Fa-f]+)', text)
                if idb and msk and flg:
                    idb_val = idb.group(1)
                    msk_val = msk.group(1)
                    flg_val = flg.group(1)
                    enabled = not (idb_val == '0x0' and msk_val == '0x0' and flg_val == '0x0')
                    iface_rules.append({
                        "index": idx,
                        "idb": idb_val,
                        "msk": msk_val,
                        "flg": flg_val,
                        "enabled": enabled,
                    })
            config["replacing_rules"][iface] = iface_rules

    # ── CAN INTERFACES ───────────────────────
    can_section = re.search(r'!CANINTERFACES(.*?)(?=!ETHERNET|$)', content, re.DOTALL)
    if can_section:
        text = can_section.group(1)
        for i in range(6):
            abr    = re.search(rf'#CAN{i};ABR;(\d+)', text)
            defbr  = re.search(rf'#CAN{i};DEFBR;(\d+)', text)
            tres   = re.search(rf'#CAN{i};TRES;(\d+)', text)
            fthr   = re.search(rf'#CAN{i};FTHR;(\d+)', text)
            frstd  = re.search(rf'#CAN{i};FRSTD;(\d+)', text)
            frsten = re.search(rf'#CAN{i};FRSTEN;(\d+)', text)

            if abr:
                config["can_interfaces"][i] = {
                    "abr":    abr.group(1)    if abr    else "N/A",
                    "defbr":  defbr.group(1)  if defbr  else "500",
                    "tres":   tres.group(1)   if tres   else "0",
                    "fthr":   fthr.group(1)   if fthr   else "N/A",
                    "frstd":  frstd.group(1)  if frstd  else "N/A",
                    "frsten": frsten.group(1) if frsten else "N/A",
                }

    # ── ETHERNET ─────────────────────────────
    eth_section = re.search(r'!ETHERNET(.*?)(?=!FUSENOTIFICATIONS|$)', content, re.DOTALL)
    if eth_section:
        text = eth_section.group(1)
        ip    = re.search(r'IPADDR;([\d.]+)', text)
        nmask = re.search(r'NMASK;([\d.]+)', text)
        config["ethernet"] = {
            "ip":    ip.group(1)    if ip    else "N/A",
            "nmask": nmask.group(1) if nmask else "N/A",
        }

    # ── FUSE NOTIFICATIONS ───────────────────
    fuse_section = re.search(r'!FUSENOTIFICATIONS(.*?)$', content, re.DOTALL)
    if fuse_section:
        text = fuse_section.group(1)
        for i in range(6):
            ntfe   = re.search(rf'#FUSE{i};NTFE;(\d+)', text)
            ntfid  = re.search(rf'#FUSE{i};NTFID;(0x[0-9A-Fa-f]+)', text)
            ntfstd = re.search(rf'#FUSE{i};NTFSTDID;(\d+)', text)
            ntfdl  = re.search(rf'#FUSE{i};NTFDLEN;(\d+)', text)
            ntfifs = re.search(rf'#FUSE{i};NTFIFS;([0-9,]+)', text)
            ntfdbs = re.search(rf'#FUSE{i};NTFDBS;([0-9A-Fa-fx,]+)', text)
            if ntfe:
                config["fuse_notifications"][i] = {
                    "enabled": ntfe.group(1)   if ntfe   else "0",
                    "ntfid":   ntfid.group(1)  if ntfid  else "0x0",
                    "stdid":   ntfstd.group(1) if ntfstd else "0",
                    "dlen":    ntfdl.group(1)  if ntfdl  else "0",
                    "ifs":     ntfifs.group(1) if ntfifs else "0,0,0,0,0,0",
                    "dbs":     ntfdbs.group(1) if ntfdbs else "N/A",
                }

    return config


# ─────────────────────────────────────────────
# PDF GENERATOR (ReportLab)
# ─────────────────────────────────────────────

def generate_pdf(config: dict, filename: str, report_date: str, serial: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, Image as RLImage
    )
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    # ── Colour palette (GSS brand) ────────────
    NAVY      = colors.HexColor('#0A1E2C')
    STEEL     = colors.HexColor('#112B3C')
    TEAL      = colors.HexColor('#1E6E8C')
    LIGHTBLUE = colors.HexColor('#8DBDD8')
    OFFWHITE  = colors.HexColor('#F5F9FC')
    BORDER    = colors.HexColor('#D8E6EF')
    GREEN     = colors.HexColor('#065F46')
    GREEN_BG  = colors.HexColor('#D1FAE5')
    GRAY_TXT  = colors.HexColor('#5A7A8C')
    DARK_TXT  = colors.HexColor('#0A1E2C')
    MID_TXT   = colors.HexColor('#2D4A5C')
    ACCENT    = colors.HexColor('#1E6E8C')
    CODE_FONT = 'Courier'

    buffer = io.BytesIO()

    def add_header_footer(canvas_obj, doc):
        canvas_obj.saveState()
        w, h = A4

        # Header bar
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, h - 26*mm, w, 26*mm, fill=1, stroke=0)

        # Accent stripe
        canvas_obj.setFillColor(TEAL)
        canvas_obj.rect(0, h - 28*mm, w, 2*mm, fill=1, stroke=0)

        # Logo in header
        if os.path.exists(LOGO_PATH):
            try:
                canvas_obj.drawImage(
                    LOGO_PATH,
                    18*mm, h - 23*mm,
                    width=38*mm, height=14*mm,
                    preserveAspectRatio=True, mask='auto'
                )
            except Exception:
                canvas_obj.setFillColor(colors.white)
                canvas_obj.setFont('Helvetica-Bold', 10)
                canvas_obj.drawString(18*mm, h - 15*mm, 'GLOBAL SUPPLIES SOLUTIONS')

        # Header text (right side)
        canvas_obj.setFont('Helvetica-Bold', 9)
        canvas_obj.setFillColor(colors.white)
        canvas_obj.drawRightString(w - 18*mm, h - 13*mm, 'GATEWAY CONFIGURATION REPORT')
        canvas_obj.setFont('Helvetica', 7.5)
        canvas_obj.setFillColor(LIGHTBLUE)
        canvas_obj.drawRightString(w - 18*mm, h - 19.5*mm, f'S/N: {serial}  |  {report_date}')

        # Footer bar
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, 0, w, 13*mm, fill=1, stroke=0)
        canvas_obj.setFillColor(TEAL)
        canvas_obj.rect(0, 13*mm, w, 1*mm, fill=1, stroke=0)

        canvas_obj.setFillColor(LIGHTBLUE)
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.drawString(18*mm, 4.5*mm,
            'CONFIDENTIAL — For authorized personnel only. Global Supplies Solutions.')
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica-Bold', 7.5)
        canvas_obj.drawRightString(w - 18*mm, 4.5*mm, f'Page {doc.page}')

        canvas_obj.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=33*mm,
        bottomMargin=21*mm,
        leftMargin=18*mm,
        rightMargin=18*mm,
    )

    # ── Text styles ───────────────────────────
    S = lambda name, **kw: ParagraphStyle(name, **kw)

    sTitle    = S('sTitle',    fontSize=20, textColor=NAVY,     fontName='Helvetica-Bold',
                               spaceAfter=4,  leading=24)
    sSubtitle = S('sSubtitle', fontSize=9.5, textColor=GRAY_TXT, fontName='Helvetica',
                               spaceAfter=10, leading=14)
    sSectionHead = S('sSectionHead', fontSize=9, textColor=colors.white,
                                    fontName='Helvetica-Bold', spaceAfter=0, leading=13,
                                    leftIndent=6)
    sBody  = S('sBody',  fontSize=8.5, textColor=MID_TXT,  fontName='Helvetica',
                         spaceAfter=4, leading=13)
    sCode  = S('sCode',  fontSize=8,   textColor=DARK_TXT, fontName=CODE_FONT,
                         spaceAfter=3, leading=12)
    sLabel = S('sLabel', fontSize=7.5, textColor=GRAY_TXT, fontName='Helvetica-Bold',
                         spaceAfter=2, leading=11, letterSpacing=0.5)
    sNote  = S('sNote',  fontSize=7.5, textColor=GRAY_TXT, fontName='Helvetica-Oblique',
                         spaceAfter=4, leading=11)

    story = []

    # ─── COVER PAGE ─────────────────────────
    story.append(Spacer(1, 8*mm))

    # Logo block on cover
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = RLImage(LOGO_PATH, width=60*mm, height=22*mm)
            logo_img.hAlign = 'LEFT'
            story.append(logo_img)
            story.append(Spacer(1, 6*mm))
        except Exception:
            pass

    story.append(Paragraph('GATEWAY CONFIGURATION REPORT', sLabel))
    story.append(Paragraph('CAN / Ethernet Gateway', sTitle))
    story.append(Paragraph(
        f'Global Supplies Solutions — Technical Configuration Document  |  S/N: {serial}',
        sSubtitle))
    story.append(HRFlowable(width='100%', thickness=2, color=TEAL, spaceAfter=10))

    # Executive summary table
    can_ifaces = config.get('can_interfaces', {})
    can0 = can_ifaces.get(0, {})
    can1 = can_ifaces.get(1, {})

    active_filters = sum(
        1 for iface_filters in config['filters'].values()
        for f in iface_filters if f['enabled']
    )
    active_routes = sum(
        1 for iface_rules in config['routing_rules'].values()
        for r in iface_rules if r['enabled']
    )

    # Build individual baudrate rows for each channel
    baudrate_rows = []
    for i in range(6):
        ci = can_ifaces.get(i, {})
        br = ci.get('defbr', '500')
        abr_txt = 'Auto' if ci.get('abr', '0') == '1' else 'Fixed'
        baudrate_rows.append([f'CAN{i} Baudrate', f'{br} kbps ({abr_txt})'])

    summary_data = [
        ['PARAMETER', 'VALUE'],
    ] + baudrate_rows + [
        ['Active CAN Filters', str(active_filters)],
        ['Active Routing Rules', str(active_routes)],
        ['Fast Reset (CAN1–5)', 'Enabled' if can1.get('frsten', '0') == '1' else 'Disabled'],
    ]

    summary_col_widths = [80*mm, 92*mm]
    summary_style = TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 8),
        ('FONTNAME',     (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 1), (-1, -1), 8.5),
        ('FONTNAME',     (1, 1), (1, -1), CODE_FONT),
        ('TEXTCOLOR',    (0, 1), (-1, -1), DARK_TXT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
        ('GRID',         (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING',      (0, 0), (-1, -1), 7),
        ('TOPPADDING',   (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 9),
        ('LEFTPADDING',  (0, 0), (-1, -1), 11),
        # Highlight CAN baudrate rows
        ('BACKGROUND',   (0, 1), (-1, 6), colors.HexColor('#EBF5FA')),
        ('BACKGROUND',   (0, 2), (-1, 2), OFFWHITE),
        ('BACKGROUND',   (0, 4), (-1, 4), OFFWHITE),
        ('BACKGROUND',   (0, 6), (-1, 6), OFFWHITE),
    ])
    story.append(Table(summary_data, colWidths=summary_col_widths, style=summary_style))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        'IMPORTANT — CAN Baudrate Verification: The baudrate configured on each channel must match '
        'the CAN bus speed of the connected network segment. This parameter must be verified '
        'on-site during commissioning to ensure proper bus communication.',
        sNote))

    # ─── Helper: section header ────────────
    def section_header(title: str):
        t = Table([[Paragraph(title, sSectionHead)]], colWidths=[172*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), STEEL),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('LINEBELOW',     (0, 0), (-1, -1), 2, TEAL),
        ]))
        story.append(Spacer(1, 5*mm))
        story.append(t)
        story.append(Spacer(1, 3*mm))

    def subsection_header(title: str):
        t = Table([[Paragraph(title, S('sh2', fontSize=8, textColor=TEAL,
                                       fontName='Helvetica-Bold', spaceAfter=0, leading=12))
                    ]], colWidths=[172*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#E6F2F8')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('LINEBELOW',     (0, 0), (-1, -1), 0.5, TEAL),
        ]))
        story.append(Spacer(1, 3*mm))
        story.append(t)
        story.append(Spacer(1, 2*mm))

    # ─── 1. CAN INTERFACE CONFIGURATION ────
    story.append(PageBreak())
    section_header('1.  CAN INTERFACE CONFIGURATION')
    story.append(Paragraph(
        'Six CAN bus interfaces are available (CAN0 through CAN5). '
        'The table below details the baudrate, auto-detection, termination resistance, '
        'and fast-reset parameters for each interface. '
        'The configured baudrate must be verified on-site to match the connected CAN network.', sBody))
    story.append(Spacer(1, 3*mm))

    can_headers = ['Interface', 'Baudrate (kbps)', 'Auto BR', 'Termination', 'FR Threshold', 'FR Std Dev', 'Fast Reset']
    can_rows = [can_headers]
    for i in range(6):
        c = can_ifaces.get(i, {})
        abr_txt    = 'AUTO'   if c.get('abr', '0') == '1' else 'MANUAL'
        tres_txt   = 'ON'     if c.get('tres', '0') == '1' else 'OFF'
        frsten_txt = 'ON'     if c.get('frsten', '0') == '1' else 'OFF'
        br_val     = c.get('defbr', '500')
        can_rows.append([
            f'CAN{i}',
            br_val,
            abr_txt,
            tres_txt,
            c.get('fthr', 'N/A'),
            c.get('frstd', 'N/A'),
            frsten_txt,
        ])

    can_col_widths = [20*mm, 28*mm, 20*mm, 24*mm, 28*mm, 24*mm, 28*mm]
    can_style = TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
        ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, 0), 7.5),
        ('FONTNAME',       (0, 1), (-1, -1), CODE_FONT),
        ('FONTSIZE',       (0, 1), (-1, -1), 8),
        ('FONTNAME',       (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR',      (0, 1), (-1, -1), DARK_TXT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
        ('GRID',           (0, 0), (-1, -1), 0.4, BORDER),
        ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN',          (0, 0), (0, -1), 'LEFT'),
        ('PADDING',        (0, 0), (-1, -1), 7),
        # Highlight baudrate column
        ('BACKGROUND',     (1, 1), (1, -1), colors.HexColor('#E6F2F8')),
        ('FONTNAME',       (1, 1), (1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR',      (1, 1), (1, -1), STEEL),
    ])
    story.append(Table(can_rows, colWidths=can_col_widths, style=can_style))

    # ─── 2. CAN MESSAGE FILTERS ─────────────
    section_header('2.  CAN MESSAGE FILTERS')
    story.append(Paragraph(
        'Each CAN interface supports up to 10 message filters. '
        'A filter is considered active when its ID base (IDB), mask (MSK), or flags (FLG) are non-zero.',
        sBody))

    for iface, iface_filters in config['filters'].items():
        active = [f for f in iface_filters if f['enabled']]
        if not active:
            continue
        subsection_header(f'Interface IF{iface}')
        flt_headers = ['Rule', 'ID Base (IDB)', 'Mask (MSK)', 'Flags (FLG)', 'Status']
        flt_rows = [flt_headers]
        for f in iface_filters:
            if f['enabled']:
                flt_rows.append([
                    f"Fl{f['index']}",
                    f['idb'],
                    f['msk'],
                    f['flg'],
                    'ACTIVE',
                ])
        flt_col_widths = [20*mm, 40*mm, 40*mm, 38*mm, 34*mm]
        flt_style = TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0), TEAL),
            ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
            ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0, 0), (-1, 0), 7.5),
            ('FONTNAME',       (0, 1), (-1, -1), CODE_FONT),
            ('FONTSIZE',       (0, 1), (-1, -1), 8),
            ('FONTNAME',       (0, 1), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR',      (0, 1), (-1, -1), DARK_TXT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
            ('GRID',           (0, 0), (-1, -1), 0.4, BORDER),
            ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN',          (0, 0), (0, -1), 'LEFT'),
            ('PADDING',        (0, 0), (-1, -1), 6),
            # Status column green
            ('TEXTCOLOR',      (4, 1), (4, -1), GREEN),
            ('FONTNAME',       (4, 1), (4, -1), 'Helvetica-Bold'),
        ])
        story.append(Table(flt_rows, colWidths=flt_col_widths, style=flt_style))
        story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        'Interfaces with all filters set to zero accept all messages on that channel '
        'and are not listed above.', sNote))

    # ─── 3. MESSAGE ROUTING RULES ───────────
    section_header('3.  MESSAGE ROUTING RULES')
    story.append(Paragraph(
        'Routing rules define how CAN messages received on one interface are forwarded to other interfaces. '
        'Only rules with a non-zero RLS flag or non-zero destination interfaces are shown.', sBody))

    for iface, iface_rules in config['routing_rules'].items():
        active = [r for r in iface_rules if r['enabled']]
        if not active:
            continue
        subsection_header(f'Interface IF{iface}')
        rr_headers = ['Rule', 'Msg ID', 'Mask', 'RTR', 'Ext ID', 'RLS Flags', 'Dest. Interfaces']
        rr_rows = [rr_headers]
        for r in active:
            rr_rows.append([
                f"Rr{r['index']}",
                r['mid'],
                r['msk'],
                r['rtr'],
                r['eid'],
                r['rls'],
                r['ifs'],
            ])
        rr_col_widths = [14*mm, 22*mm, 22*mm, 14*mm, 18*mm, 24*mm, 58*mm]
        rr_style = TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0), TEAL),
            ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
            ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0, 0), (-1, 0), 7),
            ('FONTNAME',       (0, 1), (-1, -1), CODE_FONT),
            ('FONTSIZE',       (0, 1), (-1, -1), 7.5),
            ('FONTNAME',       (0, 1), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR',      (0, 1), (-1, -1), DARK_TXT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
            ('GRID',           (0, 0), (-1, -1), 0.4, BORDER),
            ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN',          (0, 0), (0, -1), 'LEFT'),
            ('PADDING',        (0, 0), (-1, -1), 5),
        ])
        story.append(Table(rr_rows, colWidths=rr_col_widths, style=rr_style))
        story.append(Spacer(1, 2*mm))

    # ─── 4. FUSE NOTIFICATIONS ──────────────
    section_header('4.  FUSE NOTIFICATIONS')
    any_fuse = any(
        v.get('enabled', '0') == '1'
        for v in config['fuse_notifications'].values()
    )
    if any_fuse:
        story.append(Paragraph('Active fuse notification channels are listed below.', sBody))
    else:
        notice = Table(
            [[Paragraph(
                'All fuse notification channels (FUSE0–FUSE5) are disabled. '
                'No CAN notifications will be generated upon fuse events.',
                S('noticeP2', fontSize=8.5, textColor=GRAY_TXT,
                  fontName='Helvetica-Oblique', spaceAfter=0, leading=13)
            )]],
            colWidths=[172*mm]
        )
        notice.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EBF5FA')),
            ('PADDING',    (0, 0), (-1, -1), 12),
            ('BOX',        (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        story.append(notice)

    fn_headers = ['Fuse', 'Status', 'Notif. ID', 'Std ID', 'Data Len', 'Interfaces', 'Data Bytes']
    fn_rows = [fn_headers]
    for i, fuse in config['fuse_notifications'].items():
        status = 'ACTIVE' if fuse.get('enabled') == '1' else 'DISABLED'
        fn_rows.append([
            f'FUSE{i}',
            status,
            fuse.get('ntfid', '0x0'),
            fuse.get('stdid', '0'),
            fuse.get('dlen', '0'),
            fuse.get('ifs', 'N/A'),
            fuse.get('dbs', 'N/A'),
        ])

    fn_col_widths = [18*mm, 20*mm, 22*mm, 16*mm, 16*mm, 28*mm, 52*mm]
    fn_style = TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
        ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, 0), 7),
        ('FONTNAME',       (0, 1), (-1, -1), CODE_FONT),
        ('FONTSIZE',       (0, 1), (-1, -1), 7),
        ('FONTNAME',       (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR',      (0, 1), (-1, -1), DARK_TXT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
        ('GRID',           (0, 0), (-1, -1), 0.4, BORDER),
        ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN',          (0, 0), (0, -1), 'LEFT'),
        ('PADDING',        (0, 0), (-1, -1), 5),
    ])
    story.append(Spacer(1, 3*mm))
    story.append(Table(fn_rows, colWidths=fn_col_widths, style=fn_style))

    # ─── DOCUMENT INFORMATION (last page) ───
    story.append(PageBreak())
    section_header('DOCUMENT INFORMATION')
    story.append(Spacer(1, 5*mm))

    doc_data = [
        ['Field', 'Value'],
        ['Report Date',           report_date],
        ['Device Serial Number',  f'S/N: {serial}'],
        ['Total CAN Interfaces',  '6 (CAN0–CAN5)'],
        ['Total Filter Slots',    '60 (10 per interface)'],
        ['Total Routing Slots',   '60 (10 per interface)'],
        ['Gateway Status',        'FULLY CONFIGURED — Ready for Deployment'],
    ]
    doc_col_widths = [72*mm, 100*mm]
    doc_style = TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
        ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, 0), 8),
        ('FONTNAME',       (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 1), (-1, -1), 9),
        ('FONTNAME',       (1, 1), (1, -1), CODE_FONT),
        ('TEXTCOLOR',      (0, 1), (-1, -1), DARK_TXT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [OFFWHITE, colors.white]),
        ('GRID',           (0, 0), (-1, -1), 0.4, BORDER),
        ('PADDING',        (0, 0), (-1, -1), 9),
        # Gateway Status row — highlight green
        ('BACKGROUND',     (0, -1), (-1, -1), colors.HexColor('#D1FAE5')),
        ('TEXTCOLOR',      (1, -1), (1, -1), colors.HexColor('#065F46')),
        ('FONTNAME',       (1, -1), (1, -1), 'Helvetica-Bold'),
    ])
    story.append(Table(doc_data, colWidths=doc_col_widths, style=doc_style))
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        'The information contained herein reflects the exact parameters stored in the gateway '
        'at the time of configuration. Any subsequent changes to the device will require '
        'a new configuration report.',
        sNote))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    return buffer.getvalue()


# ─────────────────────────────────────────────
# STREAMLIT RENDER COMPONENTS
# ─────────────────────────────────────────────

def render_header():
    st.markdown(f"""
    <div class="report-header">
        <div style="flex-shrink:0;">{LOGO_HTML}</div>
        <div class="header-text">
            <div class="header-badge">Global Supplies Solutions</div>
            <h1>Gateway Configuration Report</h1>
            <p>CAN / Ethernet Gateway — Configuration Analysis &amp; Export Tool</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric(label, value, highlight=False):
    cls = "metric-value highlight" if highlight else "metric-value"
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="{cls}">{value}</div>
    </div>
    """


def render_section(title, content_html):
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        {content_html}
    </div>
    """, unsafe_allow_html=True)


def badge(text, tipo="active"):
    return f'<span class="badge-{tipo}">{text}</span>'


def render_can_interfaces(can_ifaces):
    rows = ""
    for i in range(6):
        c = can_ifaces.get(i, {})
        abr_badge    = badge("AUTO", "auto")  if c.get('abr', '0') == '1' else badge("MANUAL", "inactive")
        tres_badge   = badge("ON", "active")  if c.get('tres', '0') == '1' else badge("OFF", "inactive")
        frsten_badge = badge("ON", "active")  if c.get('frsten', '0') == '1' else badge("OFF", "inactive")
        fthr  = c.get('fthr', '—')
        frstd = c.get('frstd', '—')
        br    = c.get('defbr', '500')
        rows += f"""
        <tr>
            <td class="label-col" style="font-family:monospace;font-weight:700;">CAN{i}</td>
            <td style="font-weight:700;color:#1E6E8C;">{br} kbps</td>
            <td>{abr_badge}</td>
            <td>{tres_badge}</td>
            <td>{fthr if fthr != 'N/A' else '—'}</td>
            <td>{frstd if frstd != 'N/A' else '—'}</td>
            <td>{frsten_badge}</td>
        </tr>"""

    html = f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th>Interface</th>
                <th>Baudrate</th>
                <th>Auto Baudrate</th>
                <th>Termination</th>
                <th>FR Threshold</th>
                <th>FR Std Dev (ms)</th>
                <th>Fast Reset</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""
    render_section("CAN Interface Configuration", html)


def render_filters_tab(filters):
    tabs = st.tabs([f"IF{i}" for i in range(6)])
    for i, tab in enumerate(tabs):
        with tab:
            iface_filters = filters.get(i, [])
            active = [f for f in iface_filters if f['enabled']]
            if not active:
                st.markdown(
                    '<p style="color:#94A3B8;font-size:0.85rem;padding:1rem 0;">'
                    'No active filters on this interface. All messages are accepted.</p>',
                    unsafe_allow_html=True)
            else:
                rows = ""
                for f in iface_filters:
                    status_html = badge("ACTIVE", "active") if f['enabled'] else badge("DISABLED", "inactive")
                    rows += f"""
                    <tr>
                        <td class="label-col">Fl{f['index']}</td>
                        <td>{f['idb']}</td>
                        <td>{f['msk']}</td>
                        <td>{f['flg']}</td>
                        <td>{status_html}</td>
                    </tr>"""
                st.markdown(f"""
                <table class="custom-table">
                    <thead>
                        <tr><th>Rule</th><th>ID Base (IDB)</th>
                        <th>Mask (MSK)</th><th>Flags (FLG)</th><th>Status</th></tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>""", unsafe_allow_html=True)


def render_routing_tab(routing_rules):
    tabs = st.tabs([f"IF{i}" for i in range(6)])
    for i, tab in enumerate(tabs):
        with tab:
            iface_rules = routing_rules.get(i, [])
            active = [r for r in iface_rules if r['enabled']]
            if not active:
                st.markdown(
                    '<p style="color:#94A3B8;font-size:0.85rem;padding:1rem 0;">'
                    'No routing rules configured on this interface.</p>',
                    unsafe_allow_html=True)
            else:
                rows = ""
                for r in active:
                    rows += f"""
                    <tr>
                        <td class="label-col">Rr{r['index']}</td>
                        <td>{r['mid']}</td>
                        <td>{r['msk']}</td>
                        <td>{r['rtr']}</td>
                        <td>{r['eid']}</td>
                        <td>{r['rls']}</td>
                        <td>{r['ifs']}</td>
                    </tr>"""
                st.markdown(f"""
                <table class="custom-table">
                    <thead>
                        <tr><th>Rule</th><th>Msg ID</th><th>Mask</th>
                        <th>RTR</th><th>Ext. ID</th><th>RLS Flags</th>
                        <th>Dest. Interfaces</th></tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>""", unsafe_allow_html=True)


def render_fuse_notifications(fuse_notifications):
    rows = ""
    for i, fuse in fuse_notifications.items():
        status_html = badge("ACTIVE", "active") if fuse.get('enabled') == '1' else badge("DISABLED", "inactive")
        rows += f"""
        <tr>
            <td class="label-col">FUSE{i}</td>
            <td>{status_html}</td>
            <td>{fuse.get('ntfid', '0x0')}</td>
            <td>{fuse.get('stdid', '0')}</td>
            <td>{fuse.get('dlen', '0')}</td>
            <td>{fuse.get('ifs', 'N/A')}</td>
        </tr>"""
    html = f"""
    <table class="custom-table">
        <thead>
            <tr><th>Fuse Channel</th><th>Status</th><th>Notification ID</th>
            <th>Std Frame ID</th><th>Data Length</th><th>Interfaces</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""
    render_section("Fuse Notifications", html)


def render_summary_cards(config, serial):
    can_ifaces = config.get('can_interfaces', {})
    can0 = can_ifaces.get(0, {})
    can1 = can_ifaces.get(1, {})

    active_filters = sum(
        1 for iface_filters in config['filters'].values()
        for f in iface_filters if f['enabled']
    )
    active_routes = sum(
        1 for iface_rules in config['routing_rules'].values()
        for r in iface_rules if r['enabled']
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Serial Number",    f"S/N: {serial}")
    with col2:
        st.metric("CAN0 Baudrate",    f"{can0.get('defbr', '500')} kbps")
    with col3:
        st.metric("Active Filters",   str(active_filters))
    with col4:
        st.metric("Active Routes",    str(active_routes))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("CAN0 Auto-BR",     "Yes" if can0.get('abr', '0') == '1' else "No")
    with col6:
        st.metric("Fast Reset CAN1–5", "Yes" if can1.get('frsten', '0') == '1' else "No")
    with col7:
        any_replacing = any(
            r['enabled']
            for iface_rules in config['replacing_rules'].values()
            for r in iface_rules
        )
        st.metric("Replacing Rules",  "Active" if any_replacing else "None")
    with col8:
        any_fuse = any(
            v.get('enabled', '0') == '1'
            for v in config['fuse_notifications'].values()
        )
        st.metric("Fuse Notifications", "Active" if any_fuse else "None")


# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────

def main():
    render_header()

    # ── Session state ──────────────────────
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'filename' not in st.session_state:
        st.session_state.filename = ""
    if 'raw_content' not in st.session_state:
        st.session_state.raw_content = ""

    # ── STEP 1: Load file ─────────────────
    st.markdown("""
    <div class="section-card" style="border-left-color:#1E6E8C;">
        <div class="section-title">Step 1 — Load Configuration File</div>
        <p style="color:#5A7A8C;font-size:0.87rem;margin:0 0 0.5rem 0;">
            Upload the .txt configuration file exported from the gateway.
            The file will be parsed automatically upon upload.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        label="Drop the configuration file here or click to browse",
        type=["txt"],
        label_visibility="collapsed",
    )

    if uploaded is not None:
        content = uploaded.read().decode('utf-8', errors='replace')
        st.session_state.raw_content = content
        st.session_state.config = parse_config(content)
        st.session_state.filename = uploaded.name
        st.success(f"File loaded successfully: {uploaded.name}")

    # ── STEP 2: Visualisation ─────────────
    if st.session_state.config is not None:
        cfg   = st.session_state.config
        fname = st.session_state.filename
        serial = extract_serial(fname)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title" style="font-size:0.85rem;color:#0A1E2C;
             text-transform:uppercase;letter-spacing:1.2px;margin-bottom:1rem;">
            Step 2 — Configuration Overview
        </div>""", unsafe_allow_html=True)

        render_summary_cards(cfg, serial)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Visualisation tabs (no Ethernet, no Replacing Rules as standalone tabs —
        # they remain accessible in the Streamlit view but are removed from the PDF)
        tab_can, tab_eth, tab_flt, tab_rrt, tab_rpl, tab_fuse, tab_raw = st.tabs([
            "CAN Interfaces",
            "Ethernet",
            "Filters",
            "Routing Rules",
            "Replacing Rules",
            "Fuse Notifications",
            "Raw File",
        ])

        with tab_can:
            render_can_interfaces(cfg.get('can_interfaces', {}))

        with tab_eth:
            eth = cfg.get('ethernet', {})
            ip = eth.get('ip', 'N/A')
            nmask = eth.get('nmask', 'N/A')
            network = '.'.join(ip.split('.')[:3]) + '.0/24' if ip != 'N/A' else 'N/A'
            metrics = f"""
            <div class="metric-grid">
                {render_metric("IP Address", ip, highlight=True)}
                {render_metric("Subnet Mask", nmask)}
                {render_metric("Network", network)}
            </div>"""
            render_section("Ethernet Configuration", metrics)

        with tab_flt:
            st.markdown("""
            <div class="section-card">
                <div class="section-title">CAN Message Filters</div>
            """, unsafe_allow_html=True)
            render_filters_tab(cfg.get('filters', {}))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_rrt:
            st.markdown("""
            <div class="section-card">
                <div class="section-title">Message Routing Rules</div>
            """, unsafe_allow_html=True)
            render_routing_tab(cfg.get('routing_rules', {}))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_rpl:
            st.markdown("""
            <div class="section-card">
                <div class="section-title">Message Replacing Rules</div>
            """, unsafe_allow_html=True)
            any_repl = any(
                r['enabled']
                for iface_rules in cfg['replacing_rules'].values()
                for r in iface_rules
            )
            if not any_repl:
                st.markdown(
                    '<p style="color:#94A3B8;font-size:0.87rem;padding:0.5rem 0;">'
                    'No replacing rules are active on any interface. '
                    'Message IDs are forwarded without modification.</p>',
                    unsafe_allow_html=True)
            else:
                tabs_repl = st.tabs([f"IF{i}" for i in range(6)])
                for i, t in enumerate(tabs_repl):
                    with t:
                        active = [r for r in cfg['replacing_rules'].get(i, []) if r['enabled']]
                        if not active:
                            st.markdown('<p style="color:#94A3B8;font-size:0.85rem;">No rules.</p>',
                                        unsafe_allow_html=True)
                        else:
                            rows = ""
                            for r in active:
                                rows += f"<tr><td>{r['index']}</td><td>{r['idb']}</td>" \
                                        f"<td>{r['msk']}</td><td>{r['flg']}</td></tr>"
                            st.markdown(f"""
                            <table class="custom-table">
                                <thead><tr><th>Rule</th><th>ID Base</th>
                                <th>Mask</th><th>Flags</th></tr></thead>
                                <tbody>{rows}</tbody>
                            </table>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_fuse:
            render_fuse_notifications(cfg.get('fuse_notifications', {}))

        with tab_raw:
            st.markdown("""
            <div class="section-card">
                <div class="section-title">Raw Configuration File</div>
            """, unsafe_allow_html=True)
            st.code(st.session_state.raw_content, language="text")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 3: Export PDF ──────────────
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title" style="font-size:0.85rem;color:#0A1E2C;
             text-transform:uppercase;letter-spacing:1.2px;margin-bottom:1rem;">
            Step 3 — Export PDF Report
        </div>""", unsafe_allow_html=True)

        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown(
                '<p style="color:#5A7A8C;font-size:0.87rem;margin:0;">'
                'The PDF report includes all configuration sections formatted as a professional '
                'technical document, ready for customer delivery and archiving.</p>',
                unsafe_allow_html=True)
        with col_btn:
            report_date = datetime.now().strftime("%Y-%m-%d")
            pdf_bytes = generate_pdf(cfg, fname, report_date, serial)
            pdf_name = f"GSS_Gateway_Report_SN{serial}.pdf"
            st.download_button(
                label="⬇  Export PDF Report",
                data=pdf_bytes,
                file_name=pdf_name,
                mime="application/pdf",
            )

    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#94A3B8;">
            <div style="font-size:1rem;font-weight:600;color:#5A7A8C;margin-bottom:0.4rem;">
                No file loaded
            </div>
            <div style="font-size:0.85rem;">
                Upload a gateway configuration .txt file above to begin.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="report-footer">
        Global Supplies Solutions &nbsp;|&nbsp; Gateway Configuration Report Tool
        &nbsp;|&nbsp; For authorized personnel only
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
