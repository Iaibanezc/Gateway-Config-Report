"""
Axiomatic Gateway Configuration Report
---------------------------------------
Aplicación Streamlit para visualizar y exportar como PDF
la configuración de un gateway Axiomatic AX141600.

Flujo: Cargar TXT → Visualizar configuración → Exportar PDF
"""

import streamlit as st
import re
import io
from datetime import datetime

# ─────────────────────────────────────────────
# Configuración de página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Axiomatic Gateway Report",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Estilos CSS globales
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general */
    .stApp {
        background-color: #F4F6F9;
    }

    /* Header principal */
    .report-header {
        background: linear-gradient(135deg, #0D1B2A 0%, #1B2A3B 60%, #1E3A5F 100%);
        color: white;
        padding: 2.5rem 3rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .report-header h1 {
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        letter-spacing: 0.5px;
        color: white !important;
    }
    .report-header p {
        font-size: 0.9rem;
        color: #A8C0D6;
        margin: 0;
        font-weight: 400;
    }
    .header-badge {
        display: inline-block;
        background-color: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: #C8DCF0;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 0.8rem;
    }

    /* Tarjetas de sección */
    .section-card {
        background: white;
        border-radius: 10px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #1E3A5F;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0D1B2A;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 1.2rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #E8ECF0;
    }

    /* Tarjetas de métrica */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
    }
    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0D1B2A;
        font-family: 'Courier New', monospace;
    }
    .metric-value.highlight {
        color: #1E3A5F;
    }

    /* Tablas personalizadas */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
    }
    .custom-table thead tr {
        background-color: #0D1B2A;
        color: white;
    }
    .custom-table thead th {
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
        letter-spacing: 0.5px;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    .custom-table tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .custom-table tbody tr:hover {
        background-color: #EBF2FB;
    }
    .custom-table tbody td {
        padding: 9px 14px;
        color: #1E293B;
        border-bottom: 1px solid #E8ECF0;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
    }
    .custom-table tbody td.label-col {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #374151;
    }

    /* Badges de estado */
    .badge-active {
        display: inline-block;
        background-color: #DCFCE7;
        color: #166534;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }
    .badge-inactive {
        display: inline-block;
        background-color: #F1F5F9;
        color: #94A3B8;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }
    .badge-auto {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1D4ED8;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }
    .badge-manual {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.68px;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }

    /* Upload zone */
    .upload-zone {
        background: white;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        transition: border-color 0.2s;
    }
    .upload-zone:hover {
        border-color: #1E3A5F;
    }
    .upload-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0D1B2A;
        margin-bottom: 0.4rem;
    }
    .upload-subtitle {
        font-size: 0.85rem;
        color: #64748B;
    }

    /* Botón de exportar */
    .stDownloadButton > button {
        background-color: #0D1B2A !important;
        color: white !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.88rem !important;
        transition: background-color 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1E3A5F !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: #64748B;
        padding: 0.6rem 1.2rem;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #0D1B2A !important;
        background-color: white !important;
        border-bottom: 2px solid #1E3A5F !important;
    }

    /* Info box */
    .info-row {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }
    .info-item {
        flex: 1;
        min-width: 160px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
    .info-key {
        font-size: 0.68rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .info-val {
        font-size: 0.9rem;
        font-weight: 600;
        color: #0D1B2A;
        margin-top: 2px;
    }

    /* Divisor */
    .divider {
        height: 1px;
        background: #E2E8F0;
        margin: 1.5rem 0;
    }

    /* Footer */
    .report-footer {
        text-align: center;
        padding: 1.5rem;
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PARSER DEL ARCHIVO DE CONFIGURACIÓN
# ─────────────────────────────────────────────

def parse_config(content: str) -> dict:
    """Parsea el contenido del archivo de configuración del gateway Axiomatic."""

    config = {
        "filters": {},
        "routing_rules": {},
        "replacing_rules": {},
        "can_interfaces": {},
        "ethernet": {},
        "fuse_notifications": {},
    }

    # ── FILTROS ──────────────────────────────
    filters_section = re.search(r'!FILTERS(.*?)(?=!ROUTINGRULES|$)', content, re.DOTALL)
    if filters_section:
        text = filters_section.group(1)
        for iface in range(6):
            iface_filters = []
            for idx in range(10):
                idb  = re.search(rf'#IF{iface};FlIDB{idx};(0x[0-9A-Fa-f]+)', text)
                msk  = re.search(rf'#IF{iface};FlMSK{idx};(0x[0-9A-Fa-f]+)', text)
                flg  = re.search(rf'#IF{iface};FlFLG{idx};(0x[0-9A-Fa-f]+)', text)
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
                mid  = re.search(rf'#IF{iface};RrMID{idx};(0x[0-9A-Fa-f]+)', text)
                msk  = re.search(rf'#IF{iface};RrMSK{idx};(0x[0-9A-Fa-f]+)', text)
                rtr  = re.search(rf'#IF{iface};RrRTR{idx};(0x[0-9A-Fa-f]+)', text)
                eid  = re.search(rf'#IF{iface};RrEID{idx};(0x[0-9A-Fa-f]+)', text)
                rls  = re.search(rf'#IF{iface};RrRLS{idx};(0x[0-9A-Fa-f]+)', text)
                ifs  = re.search(rf'#IF{iface};RrIFS{idx};([0-9,]+)', text)
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
                idb  = re.search(rf'#IF{iface};DrIDB{idx};(0x[0-9A-Fa-f]+)', text)
                msk  = re.search(rf'#IF{iface};DrMSK{idx};(0x[0-9A-Fa-f]+)', text)
                flg  = re.search(rf'#IF{iface};DrFLG{idx};(0x[0-9A-Fa-f]+)', text)
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
            abr   = re.search(rf'#CAN{i};ABR;(\d+)', text)
            defbr = re.search(rf'#CAN{i};DEFBR;(\d+)', text)   # kbps, always present
            tres  = re.search(rf'#CAN{i};TRES;(\d+)', text)
            fthr  = re.search(rf'#CAN{i};FTHR;(\d+)', text)
            frstd = re.search(rf'#CAN{i};FRSTD;(\d+)', text)
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
# GENERADOR DE PDF (ReportLab)
# ─────────────────────────────────────────────

def generate_pdf(config: dict, filename: str, report_date: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import Frame, PageTemplate
    from reportlab.pdfgen import canvas as rl_canvas

    # Paleta de colores
    NAVY      = colors.HexColor('#0D1B2A')
    STEEL     = colors.HexColor('#1E3A5F')
    LIGHTBLUE = colors.HexColor('#A8C0D6')
    OFFWHITE  = colors.HexColor('#F8FAFC')
    BORDER    = colors.HexColor('#E2E8F0')
    GREEN     = colors.HexColor('#166534')
    GREEN_BG  = colors.HexColor('#DCFCE7')
    GRAY_TXT  = colors.HexColor('#64748B')
    DARK_TXT  = colors.HexColor('#0D1B2A')
    MID_TXT   = colors.HexColor('#374151')
    CODE_FONT = 'Courier'

    buffer = io.BytesIO()

    def add_header_footer(canvas_obj, doc):
        canvas_obj.saveState()
        w, h = A4

        # Header bar
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, h - 28*mm, w, 28*mm, fill=1, stroke=0)

        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica-Bold', 11)
        canvas_obj.drawString(20*mm, h - 12*mm, 'AXIOMATIC GATEWAY')
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(LIGHTBLUE)
        canvas_obj.drawString(20*mm, h - 19*mm, 'Configuration Report — AX141600 Series')

        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.white)
        canvas_obj.drawRightString(w - 20*mm, h - 12*mm, report_date)
        canvas_obj.drawRightString(w - 20*mm, h - 19*mm, filename)

        # Footer bar
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, 0, w, 14*mm, fill=1, stroke=0)
        canvas_obj.setFillColor(LIGHTBLUE)
        canvas_obj.setFont('Helvetica', 7.5)
        canvas_obj.drawString(20*mm, 5*mm,
            'CONFIDENTIAL — For authorized personnel only. Axiomatic Technologies Ltd.')
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica-Bold', 7.5)
        canvas_obj.drawRightString(w - 20*mm, 5*mm,
            f'Page {doc.page}')

        canvas_obj.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=35*mm,
        bottomMargin=22*mm,
        leftMargin=20*mm,
        rightMargin=20*mm,
    )

    # ── Estilos de texto ──────────────────────
    styles = getSampleStyleSheet()

    S = lambda name, **kw: ParagraphStyle(name, **kw)

    sTitle = S('sTitle', fontSize=18, textColor=NAVY, fontName='Helvetica-Bold',
               spaceAfter=4, leading=22)
    sSubtitle = S('sSubtitle', fontSize=10, textColor=GRAY_TXT, fontName='Helvetica',
                  spaceAfter=10, leading=14)
    sSectionHead = S('sSectionHead', fontSize=9, textColor=colors.white,
                     fontName='Helvetica-Bold', spaceAfter=0, leading=13,
                     leftIndent=6, spaceBefore=0)
    sBody = S('sBody', fontSize=8.5, textColor=MID_TXT, fontName='Helvetica',
              spaceAfter=4, leading=13)
    sCode = S('sCode', fontSize=8, textColor=DARK_TXT, fontName=CODE_FONT,
              spaceAfter=3, leading=12)
    sLabel = S('sLabel', fontSize=7.5, textColor=GRAY_TXT, fontName='Helvetica-Bold',
               spaceAfter=2, leading=11, letterSpacing=0.5)
    sNote = S('sNote', fontSize=7.5, textColor=GRAY_TXT, fontName='Helvetica-Oblique',
              spaceAfter=4, leading=11)

    story = []

    # ─────────────── PORTADA ───────────────
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph('CONFIGURATION REPORT', sLabel))
    story.append(Paragraph('Gateway CAN/Ethernet', sTitle))
    story.append(Paragraph('Axiomatic AX141600 Series — Technical Configuration Document', sSubtitle))
    story.append(HRFlowable(width='100%', thickness=2, color=STEEL, spaceAfter=10))

    # Tabla resumen ejecutivo
    eth = config.get('ethernet', {})
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

    summary_data = [
        ['PARAMETER', 'VALUE', 'PARAMETER', 'VALUE'],
        ['IP Address',      eth.get('ip', 'N/A'),
         'Subnet Mask',     eth.get('nmask', 'N/A')],
        ['CAN0 Baudrate',   f"{can0.get('defbr','500')} kbps",
         'CAN0 Auto-BR',    'Enabled' if can0.get('abr','0') == '1' else 'Disabled'],
        ['CAN1-5 Baudrate', f"{can1.get('defbr','500')} kbps",
         'Active Filters',  str(active_filters)],
        ['Active Routes',   str(active_routes),
         'Fast Reset',      'Enabled (CAN1-5)' if can1.get('frsten','0') == '1' else 'Disabled'],
    ]

    summary_col_widths = [42*mm, 40*mm, 42*mm, 40*mm]
    summary_style = TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 7.5),
        ('FONTNAME',     (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',     (2,1), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,1), (-1,-1), 8.5),
        ('FONTNAME',     (1,1), (1,-1), CODE_FONT),
        ('FONTNAME',     (3,1), (3,-1), CODE_FONT),
        ('TEXTCOLOR',    (0,1), (-1,-1), DARK_TXT),
        ('BACKGROUND',   (0,1), (-1,-1), OFFWHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [OFFWHITE, colors.white]),
        ('GRID',         (0,0), (-1,-1), 0.5, BORDER),
        ('PADDING',      (0,0), (-1,-1), 6),
        ('TOPPADDING',   (0,0), (-1,0), 8),
        ('BOTTOMPADDING',(0,0), (-1,0), 8),
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
    ])
    story.append(Table(summary_data, colWidths=summary_col_widths, style=summary_style))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        'This document presents the complete technical configuration of the Axiomatic gateway at the time of setup. '
        'All parameters have been verified and exported directly from the device configuration file.',
        sNote))

    # ─────────────── Helper: section header ───
    def section_header(title: str):
        t = Table([[Paragraph(title, sSectionHead)]], colWidths=[170*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), NAVY),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(Spacer(1, 5*mm))
        story.append(t)
        story.append(Spacer(1, 3*mm))

    def subsection_header(title: str):
        t = Table([[Paragraph(title, S('sh2', fontSize=8, textColor=STEEL,
                                       fontName='Helvetica-Bold', spaceAfter=0, leading=12))
                    ]], colWidths=[170*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF2FB')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, STEEL),
        ]))
        story.append(Spacer(1, 3*mm))
        story.append(t)
        story.append(Spacer(1, 2*mm))

    # ─────────────── 1. CAN INTERFACES ────────────────
    story.append(PageBreak())
    section_header('1.  CAN INTERFACE CONFIGURATION')
    story.append(Paragraph(
        'Six CAN bus interfaces are available (CAN0 through CAN5). '
        'The table below details the baudrate, auto-detection, termination resistance, '
        'and fast-reset parameters for each interface.', sBody))
    story.append(Spacer(1, 3*mm))

    can_headers = ['Interface', 'Auto BR', 'Baudrate (kbps)',
                   'Termination', 'FR Threshold', 'FR Std Dev', 'Fast Reset']
    can_rows = [can_headers]
    for i in range(6):
        c = can_ifaces.get(i, {})
        abr_txt    = 'AUTO'   if c.get('abr','0') == '1' else 'MANUAL'
        tres_txt   = 'ON'     if c.get('tres','0') == '1' else 'OFF'
        frsten_txt = 'ON'     if c.get('frsten','0') == '1' else 'OFF'
        can_rows.append([
            f'CAN{i}',
            abr_txt,
            c.get('defbr', '500'),
            tres_txt,
            c.get('fthr', 'N/A'),
            c.get('frstd', 'N/A'),
            frsten_txt,
        ])

    can_col_widths = [20*mm, 20*mm, 30*mm, 24*mm, 25*mm, 25*mm, 24*mm]
    can_style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), STEEL),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 7.5),
        ('FONTNAME',      (0,1), (-1,-1), CODE_FONT),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',         (0,0), (0,-1), 'LEFT'),
        ('PADDING',       (0,0), (-1,-1), 6),
    ])
    story.append(Table(can_rows, colWidths=can_col_widths, style=can_style))

    # ─────────────── 2. ETHERNET ────────────────
    section_header('2.  ETHERNET CONFIGURATION')
    story.append(Paragraph(
        'The gateway communicates with the host network via Ethernet. '
        'The following static IP parameters are configured on the device.', sBody))
    story.append(Spacer(1, 3*mm))

    eth_data = [
        ['Parameter', 'Value'],
        ['IP Address',   eth.get('ip', 'N/A')],
        ['Subnet Mask',  eth.get('nmask', 'N/A')],
        ['Network',      f"{'.'.join(eth.get('ip','0.0.0.0').split('.')[:3])}.0 / 24"],
    ]
    eth_col_widths = [60*mm, 110*mm]
    eth_style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), STEEL),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 8),
        ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,1), (-1,-1), 9),
        ('FONTNAME',      (1,1), (1,-1), CODE_FONT),
        ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
        ('PADDING',       (0,0), (-1,-1), 8),
    ])
    story.append(Table(eth_data, colWidths=eth_col_widths, style=eth_style))

    # ─────────────── 3. FILTROS ────────────────
    section_header('3.  CAN MESSAGE FILTERS')
    story.append(Paragraph(
        'Each CAN interface supports up to 10 message filters. '
        'A filter is considered active when its ID base (IDB), mask (MSK), or flags (FLG) are non-zero. '
        'Inactive filters (all fields zero) are omitted from this report.', sBody))

    for iface, iface_filters in config['filters'].items():
        active = [f for f in iface_filters if f['enabled']]
        if not active:
            continue
        subsection_header(f'Interface IF{iface}')
        flt_headers = ['Rule', 'ID Base (IDB)', 'Mask (MSK)', 'Flags (FLG)', 'Status']
        flt_rows = [flt_headers]
        for f in iface_filters:
            status = 'ACTIVE' if f['enabled'] else 'DISABLED'
            if f['enabled']:
                flt_rows.append([
                    f"Fl{f['index']}",
                    f['idb'],
                    f['msk'],
                    f['flg'],
                    status,
                ])
        flt_col_widths = [20*mm, 38*mm, 38*mm, 38*mm, 36*mm]
        flt_style = TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), STEEL),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 7.5),
            ('FONTNAME',      (0,1), (-1,-1), CODE_FONT),
            ('FONTSIZE',      (0,1), (-1,-1), 8),
            ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('ALIGN',         (0,0), (0,-1), 'LEFT'),
            ('PADDING',       (0,0), (-1,-1), 6),
        ])
        story.append(Table(flt_rows, colWidths=flt_col_widths, style=flt_style))
        story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        'Interfaces with all filters set to zero (IF1–IF5, rules Fl1–Fl9) accept all messages on that channel '
        'and are not listed above.', sNote))

    # ─────────────── 4. ROUTING RULES ────────────
    section_header('4.  MESSAGE ROUTING RULES')
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
        rr_col_widths = [14*mm, 22*mm, 22*mm, 14*mm, 18*mm, 22*mm, 58*mm]
        rr_style = TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), STEEL),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 7),
            ('FONTNAME',      (0,1), (-1,-1), CODE_FONT),
            ('FONTSIZE',      (0,1), (-1,-1), 7.5),
            ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('ALIGN',         (0,0), (0,-1), 'LEFT'),
            ('PADDING',       (0,0), (-1,-1), 5),
        ])
        story.append(Table(rr_rows, colWidths=rr_col_widths, style=rr_style))
        story.append(Spacer(1, 2*mm))

    # ─────────────── 5. REPLACING RULES ────────────
    section_header('5.  MESSAGE REPLACING RULES')
    any_replacing = any(
        r['enabled']
        for iface_rules in config['replacing_rules'].values()
        for r in iface_rules
    )
    if any_replacing:
        story.append(Paragraph(
            'The following replacing rules modify the CAN ID of matched messages before forwarding.', sBody))
        for iface, iface_rules in config['replacing_rules'].items():
            active = [r for r in iface_rules if r['enabled']]
            if not active:
                continue
            subsection_header(f'Interface IF{iface}')
            dr_headers = ['Rule', 'ID Base', 'Mask', 'Flags']
            dr_rows = [dr_headers]
            for r in active:
                dr_rows.append([f"Dr{r['index']}", r['idb'], r['msk'], r['flg']])
            dr_col_widths = [25*mm, 45*mm, 45*mm, 55*mm]
            dr_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), STEEL),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,0), 7.5),
                ('FONTNAME',   (0,1), (-1,-1), CODE_FONT),
                ('FONTSIZE',   (0,1), (-1,-1), 8),
                ('TEXTCOLOR',  (0,1), (-1,-1), DARK_TXT),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [OFFWHITE, colors.white]),
                ('GRID',       (0,0), (-1,-1), 0.4, BORDER),
                ('PADDING',    (0,0), (-1,-1), 6),
            ])
            story.append(Table(dr_rows, colWidths=dr_col_widths, style=dr_style))
    else:
        notice = Table(
            [[Paragraph(
                'No replacing rules are active on any interface. '
                'CAN message IDs are forwarded without modification.',
                S('noticeP', fontSize=8.5, textColor=GRAY_TXT,
                  fontName='Helvetica-Oblique', spaceAfter=0, leading=13)
            )]],
            colWidths=[170*mm]
        )
        notice.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('PADDING',    (0,0), (-1,-1), 12),
            ('BOX',        (0,0), (-1,-1), 0.5, BORDER),
        ]))
        story.append(notice)

    # ─────────────── 6. FUSE NOTIFICATIONS ────────────
    section_header('6.  FUSE NOTIFICATIONS')
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
            colWidths=[170*mm]
        )
        notice.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('PADDING',    (0,0), (-1,-1), 12),
            ('BOX',        (0,0), (-1,-1), 0.5, BORDER),
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

    fn_col_widths = [18*mm, 20*mm, 20*mm, 16*mm, 16*mm, 28*mm, 52*mm]
    fn_style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), STEEL),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 7),
        ('FONTNAME',      (0,1), (-1,-1), CODE_FONT),
        ('FONTSIZE',      (0,1), (-1,-1), 7),
        ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',         (0,0), (0,-1), 'LEFT'),
        ('PADDING',       (0,0), (-1,-1), 5),
    ])
    story.append(Spacer(1, 3*mm))
    story.append(Table(fn_rows, colWidths=fn_col_widths, style=fn_style))

    # ─────────────── Página final ────────────────
    story.append(PageBreak())
    section_header('DOCUMENT INFORMATION')
    story.append(Spacer(1, 5*mm))
    doc_data = [
        ['Field', 'Value'],
        ['Report Generated',   report_date],
        ['Source File',        filename],
        ['Device Series',      'Axiomatic AX141600'],
        ['Total CAN Interfaces', '6 (CAN0–CAN5)'],
        ['Total Filter Slots', '60 (10 per interface)'],
        ['Total Routing Slots','60 (10 per interface)'],
        ['Document Status',    'FINAL — For delivery to customer'],
    ]
    doc_col_widths = [70*mm, 100*mm]
    doc_style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 8),
        ('FONTNAME',      (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,1), (-1,-1), 9),
        ('FONTNAME',      (1,1), (1,-1), CODE_FONT),
        ('TEXTCOLOR',     (0,1), (-1,-1), DARK_TXT),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [OFFWHITE, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
        ('PADDING',       (0,0), (-1,-1), 9),
    ])
    story.append(Table(doc_data, colWidths=doc_col_widths, style=doc_style))
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        'This report was automatically generated from the device configuration file. '
        'The information contained herein reflects the exact parameters stored in the gateway '
        'at the time of configuration. Any subsequent changes to the device will require a '
        'new configuration export and report generation.',
        sNote))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    return buffer.getvalue()


# ─────────────────────────────────────────────
# COMPONENTES DE VISUALIZACIÓN (Streamlit)
# ─────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="report-header">
        <div class="header-badge">Axiomatic Technologies</div>
        <h1>Gateway Configuration Report</h1>
        <p>AX141600 Series — CAN/Ethernet Gateway | Configuration Analysis & Export Tool</p>
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
        abr_badge    = badge("AUTO", "auto")    if c.get('abr','0') == '1' else badge("MANUAL", "inactive")
        tres_badge   = badge("ON", "active")    if c.get('tres','0') == '1' else badge("OFF", "inactive")
        frsten_badge = badge("ON", "active")    if c.get('frsten','0') == '1' else badge("OFF", "inactive")
        fthr  = c.get('fthr', '—')
        frstd = c.get('frstd','—')
        rows += f"""
        <tr>
            <td class="label-col" style="font-family:monospace;font-weight:700;">CAN{i}</td>
            <td>{abr_badge}</td>
            <td>{c.get('defbr','500')} kbps</td>
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
                <th>Auto Baudrate</th>
                <th>Default Baudrate</th>
                <th>Termination</th>
                <th>FR Threshold</th>
                <th>FR Std Dev (ms)</th>
                <th>Fast Reset</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""
    render_section("CAN Interface Configuration", html)


def render_ethernet(eth):
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
            <td>{fuse.get('ntfid','0x0')}</td>
            <td>{fuse.get('stdid','0')}</td>
            <td>{fuse.get('dlen','0')}</td>
            <td>{fuse.get('ifs','N/A')}</td>
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


def render_summary_cards(config):
    can_ifaces = config.get('can_interfaces', {})
    eth = config.get('ethernet', {})
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
    any_replacing = any(
        r['enabled']
        for iface_rules in config['replacing_rules'].values()
        for r in iface_rules
    )
    any_fuse = any(
        v.get('enabled', '0') == '1'
        for v in config['fuse_notifications'].values()
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("IP Address",       eth.get('ip', 'N/A'))
    with col2:
        st.metric("CAN Baudrate",     f"{can0.get('defbr','500')} kbps")
    with col3:
        st.metric("Active Filters",   str(active_filters))
    with col4:
        st.metric("Active Routes",    str(active_routes))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("CAN0 Auto-BR",     "Yes" if can0.get('abr','0') == '1' else "No")
    with col6:
        st.metric("Fast Reset CAN1-5","Yes" if can1.get('frsten','0') == '1' else "No")
    with col7:
        st.metric("Replacing Rules",  "Active" if any_replacing else "None")
    with col8:
        st.metric("Fuse Notifications","Active" if any_fuse else "None")


# ─────────────────────────────────────────────
# APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────

def main():
    render_header()

    # ── Estado de sesión ──────────────────────
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'filename' not in st.session_state:
        st.session_state.filename = ""
    if 'raw_content' not in st.session_state:
        st.session_state.raw_content = ""

    # ── PASO 1: Carga del archivo ─────────────
    st.markdown("""
    <div class="section-card" style="border-left-color:#1E3A5F;">
        <div class="section-title">Step 1 — Load Configuration File</div>
        <p style="color:#64748B;font-size:0.87rem;margin:0 0 0.5rem 0;">
            Upload the .txt configuration file exported from the Axiomatic gateway.
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

    # ── PASO 2: Visualización ─────────────────
    if st.session_state.config is not None:
        cfg = st.session_state.config
        fname = st.session_state.filename

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title" style="font-size:0.85rem;color:#0D1B2A;
             text-transform:uppercase;letter-spacing:1.2px;margin-bottom:1rem;">
            Step 2 — Configuration Overview
        </div>""", unsafe_allow_html=True)

        render_summary_cards(cfg)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Tabs de visualización
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
            render_ethernet(cfg.get('ethernet', {}))

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

        # ── PASO 3: Exportar PDF ──────────────
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title" style="font-size:0.85rem;color:#0D1B2A;
             text-transform:uppercase;letter-spacing:1.2px;margin-bottom:1rem;">
            Step 3 — Export PDF Report
        </div>""", unsafe_allow_html=True)

        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown(
                '<p style="color:#64748B;font-size:0.87rem;margin:0;">'
                'The PDF report will include all configuration sections formatted as a '
                'professional technical document. Suitable for customer delivery and archiving.</p>',
                unsafe_allow_html=True)
        with col_btn:
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            pdf_bytes = generate_pdf(cfg, fname, report_date)
            pdf_name = fname.replace('.txt', '_report.pdf') if fname.endswith('.txt') else 'gateway_report.pdf'
            st.download_button(
                label="Export PDF Report",
                data=pdf_bytes,
                file_name=pdf_name,
                mime="application/pdf",
            )

    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#94A3B8;">
            <div style="font-size:1rem;font-weight:600;color:#64748B;margin-bottom:0.4rem;">
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
        Axiomatic Gateway Configuration Report Tool &nbsp;|&nbsp;
        AX141600 Series &nbsp;|&nbsp; Internal Use Only
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
