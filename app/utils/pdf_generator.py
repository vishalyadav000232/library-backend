from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from datetime import datetime
import tempfile
import os


def generate_professional_pdf(data, filename, report_type, start_date, end_date):

    file_path = os.path.join(tempfile.gettempdir(), filename)

    page_size = pagesizes.landscape(pagesizes.A4)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=page_size,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # -----------------------
    # Custom Styles
    # -----------------------

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#E57C31"),
        spaceAfter=6
    )

    sub_header_style = ParagraphStyle(
        "SubHeaderStyle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=10
    )

    normal_style = styles["Normal"]

    wrap_style = ParagraphStyle(
        "WrapStyle",
        parent=styles["Normal"],
        fontSize=12,
        leading=12,
        wordWrap='CJK'
    )

  

    elements.append(Paragraph("YADAV LIBRARY", header_style))
    elements.append(Paragraph("Admin Analytics Report", sub_header_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Report Type:</b> {report_type.upper()}", normal_style))
    elements.append(Paragraph(f"<b>Date Range:</b> {start_date} to {end_date}", normal_style))
    elements.append(
        Paragraph(
            f"<b>Generated At:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
            normal_style
        )
    )

    elements.append(Spacer(1, 20))

   

    total_records = len(data)

    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Total Records: {total_records}", normal_style))
    elements.append(Spacer(1, 20))

    

    if not data:
        elements.append(Paragraph("No Data Found", normal_style))
        doc.build(elements)
        return file_path

    headers = list(data[0].keys())
    table_data = []

    # Header row
    table_data.append(
        [Paragraph(f"<b>{h}</b>", wrap_style) for h in headers]
    )

    # Data rows
    for row in data:
        row_data = []
        for h in headers:
            value = str(row.get(h, ""))

            # Trim long UUID for readability
            if h.lower() == "id" and len(value) > 15:
                value = value[:15] + "..."

            row_data.append(Paragraph(value, wrap_style))
        table_data.append(row_data)

    # Column width distribution
    available_width = doc.width
    col_widths = []

    for h in headers:
        h_lower = h.lower()

        if h_lower == "id":
            col_widths.append(available_width * 0.34)
        elif "email" in h_lower:
            col_widths.append(available_width * 0.22)
        elif "name" in h_lower:
            col_widths.append(available_width * 0.15)
        elif "date" in h_lower:
            col_widths.append(available_width * 0.14)
        else:
            col_widths.append(available_width * 0.13)

    # Normalize widths
    total_width = sum(col_widths)
    if total_width > available_width:
        scale = available_width / total_width
        col_widths = [w * scale for w in col_widths]

    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E57C31")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.whitesmoke,
            colors.lightgrey
        ])
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph("Confidential Document - Yadav Library", styles["Italic"])
    )

   

    def add_page_number(canvas, doc):
        page_width = page_size[0]
        canvas.drawCentredString(
            page_width / 2,
            15,
            f"Page {doc.page}"
        )

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    return file_path
