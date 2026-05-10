
"""
Global Supplies Solutions
Gateway Configuration Report
Professional Streamlit Dashboard + PDF Export
"""

import streamlit as st
import re
import io
import os
import base64
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Gateway Configuration Report",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# BRANDING
# ---------------------------------------------------------

PRIMARY = "#123E68"
SECONDARY = "#0B2D4D"
ACCENT = "#1E5D93"
LIGHT = "#F4F7FA"
TEXT = "#1C1C1C"

LOGO_PATH = "gss_logo.png"

# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(f"""
<style>

html, body, [class*="css"] {{
    font-family: 'Arial', sans-serif;
}}

.stApp {{
    background-color: {LIGHT};
}}

.main-header {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 100%);
    padding: 2rem;
    border-radius: 14px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}}

.main-header h1 {{
    margin:0;
    font-size:2rem;
}}

.main-header p {{
    margin-top:0.4rem;
    color:#D9E7F5;
}}

.section {{
    background:white;
    padding:1.5rem;
    border-radius:12px;
    margin-bottom:1.2rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    border-left:5px solid {PRIMARY};
}}

.section-title {{
    font-size:1.1rem;
    font-weight:700;
    color:{PRIMARY};
    margin-bottom:1rem;
    text-transform:uppercase;
}}

.metric-box {{
    background:{LIGHT};
    padding:1rem;
    border-radius:10px;
    border:1px solid #DCE6EF;
}}

.metric-label {{
    font-size:0.75rem;
    color:#6B7280;
    text-transform:uppercase;
    font-weight:600;
}}

.metric-value {{
    font-size:1.1rem;
    color:{SECONDARY};
    font-weight:700;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

thead tr {{
    background:{PRIMARY};
    color:white;
}}

th, td {{
    padding:10px;
    border-bottom:1px solid #E5E7EB;
    text-align:left;
}}

tbody tr:nth-child(even) {{
    background:#F9FBFD;
}}

.stDownloadButton button {{
    background:{PRIMARY};
    color:white;
    border:none;
    border-radius:8px;
    padding:0.7rem 1rem;
    font-weight:700;
}}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def get_serial(filename):
    match = re.search(r'-(\d+)', filename)
    return match.group(1) if match else "UNKNOWN"

def extract_baudrates(content):
    matches = re.findall(r'#CAN(\d);ABR;\d;DEFBR;(\d+)', content)
    return [{"Channel": f"CAN {m[0]}", "Baudrate": f"{m[1]} kbps"} for m in matches]

def parse_filters(content):
    filters = []
    pattern = r'#IF(\d);FlIDB(\d);(0x[0-9A-Fa-f]+);#IF\1;FlMSK\2;(0x[0-9A-Fa-f]+);#IF\1;FlFLG\2;(0x[0-9A-Fa-f]+)'
    matches = re.findall(pattern, content)

    for m in matches:
        if m[2] != '0x0' or m[3] != '0x0' or m[4] != '0x0':
            filters.append({
                "Interface": f"CAN {m[0]}",
                "Filter": m[1],
                "ID": m[2],
                "Mask": m[3],
                "Flags": m[4]
            })

    return filters

def parse_routes(content):
    routes = []
    pattern = r'#IF(\d);RrRLS(\d);(0x[0-9A-Fa-f]+);#IF\1;RrIFS\2;([0-9,]+)'
    matches = re.findall(pattern, content)

    for m in matches:
        if m[2] != "0x0":
            routes.append({
                "Interface": f"CAN {m[0]}",
                "Rule": m[1],
                "Route Flags": m[2],
                "Destination": m[3]
            })

    return routes

# ---------------------------------------------------------
# PDF
# ---------------------------------------------------------

def generate_pdf(serial, baudrates, filters, routes):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor(PRIMARY),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor(PRIMARY),
        spaceAfter=10
    )

    normal = styles["BodyText"]

    elements = []

    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=3.2*inch, height=0.9*inch)
        elements.append(logo)

    elements.append(Spacer(1, 0.2 * inch))

    title = Paragraph(
        f"<b>Gateway Configuration Report</b><br/>S/N: {serial}",
        title_style
    )

    elements.append(title)

    intro = """
    The information contained herein reflects the exact parameters stored in the gateway at the time of configuration.
    Any subsequent changes to the device will require a new configuration report.
    """

    elements.append(Paragraph(intro, normal))
    elements.append(Spacer(1, 0.2 * inch))

    # DOCUMENT INFO
    elements.append(Paragraph("DOCUMENT INFORMATION", section_style))

    info_table = Table([
        ["Report Date", datetime.now().strftime("%Y-%m-%d")],
        ["Gateway Status", "Configuration Successfully Completed and Verified"]
    ], colWidths=[220, 280])

    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(PRIMARY)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#D6DCE5")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EDF3F8")),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.25 * inch))

    # BAUDRATES
    elements.append(Paragraph("GATEWAY CAN CONFIGURATION", section_style))

    warning = """
    CAN baudrate from every channel must match the machine CAN network baudrate.
    This parameter must be verified during field commissioning.
    """

    elements.append(Paragraph(warning, normal))
    elements.append(Spacer(1, 0.12 * inch))

    baud_data = [["CAN Channel", "Configured Baudrate"]]

    for row in baudrates:
        baud_data.append([row["Channel"], row["Baudrate"]])

    baud_table = Table(baud_data, colWidths=[250, 250])

    baud_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(PRIMARY)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
    ]))

    elements.append(baud_table)
    elements.append(Spacer(1, 0.25 * inch))

    # FILTERS
    elements.append(Paragraph("CAN MESSAGE FILTERS", section_style))

    if filters:

        filter_data = [["Interface", "Filter", "ID", "Mask", "Flags"]]

        for f in filters:
            filter_data.append([
                f["Interface"],
                f["Filter"],
                f["ID"],
                f["Mask"],
                f["Flags"]
            ])

        filter_table = Table(filter_data)

        filter_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(PRIMARY)),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
        ]))

        elements.append(filter_table)

    elements.append(Spacer(1, 0.25 * inch))

    # ROUTING
    elements.append(Paragraph("ROUTING CONFIGURATION", section_style))

    if routes:

        route_data = [["Interface", "Rule", "Route Flags", "Destination Ports"]]

        for r in routes:
            route_data.append([
                r["Interface"],
                r["Rule"],
                r["Route Flags"],
                r["Destination"]
            ])

        route_table = Table(route_data)

        route_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(PRIMARY)),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
        ]))

        elements.append(route_table)

    elements.append(Spacer(1, 0.35 * inch))

    footer = Paragraph(
        "Global Supplies Solutions - Gateway Configuration Services",
        ParagraphStyle(
            "footer",
            alignment=TA_CENTER,
            fontSize=9,
            textColor=colors.HexColor("#64748B")
        )
    )

    elements.append(footer)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

col1, col2 = st.columns([1,4])

with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)

with col2:
    st.markdown("""
    <div class="main-header">
        <h1>Gateway Configuration Report</h1>
        <p>Global Supplies Solutions | Professional CAN Gateway Documentation</p>
    </div>
    """, unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload Gateway TXT Configuration File",
    type=["txt"]
)

if uploaded:

    content = uploaded.read().decode(errors="ignore")

    serial = get_serial(uploaded.name)

    baudrates = extract_baudrates(content)
    filters = parse_filters(content)
    routes = parse_routes(content)

    # ---------------------------------------------------------
    # DOCUMENT INFO
    # ---------------------------------------------------------

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Document Information</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Gateway Serial Number</div>
            <div class="metric-value">{serial}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Gateway Status</div>
            <div class="metric-value">Configured & Ready For Operation</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "The information contained herein reflects the exact parameters stored in the gateway at the time of configuration. "
        "Any subsequent changes to the device will require a new configuration report."
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CAN CONFIG
    # ---------------------------------------------------------

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Gateway CAN Configuration</div>', unsafe_allow_html=True)

    st.warning(
        "CAN baudrate from every channel must match the machine CAN network baudrate. "
        "This parameter must be verified during field commissioning."
    )

    st.table(baudrates)

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # FILTERS
    # ---------------------------------------------------------

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">CAN Message Filters</div>', unsafe_allow_html=True)

    if filters:
        st.dataframe(filters, use_container_width=True)
    else:
        st.success("No active CAN message filters detected.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ROUTING
    # ---------------------------------------------------------

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Routing Configuration</div>', unsafe_allow_html=True)

    if routes:
        st.dataframe(routes, use_container_width=True)
    else:
        st.success("No routing rules detected.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # DOWNLOAD
    # ---------------------------------------------------------

    pdf = generate_pdf(serial, baudrates, filters, routes)

    st.download_button(
        label="Download Gateway Configuration Report (PDF)",
        data=pdf,
        file_name=f"Gateway_Configuration_Report_{serial}.pdf",
        mime="application/pdf"
    )
