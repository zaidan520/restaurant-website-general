from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_booking_pdf(data: dict, code: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1f2a1d'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4b5b47'),
        spaceAfter=8
    )

    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("RESERVATION RECEIPT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Reservation Code:</b> {code}", bold_style))
    story.append(Paragraph(f"<b>Guest Name:</b> {data.get('name')}", body_style))
    story.append(Paragraph(f"<b>Email Address:</b> {data.get('email')}", body_style))
    story.append(Paragraph(f"<b>Phone Number:</b> {data.get('phone')}", body_style))
    story.append(Paragraph(f"<b>Date:</b> {data.get('date')}", body_style))
    story.append(Paragraph(f"<b>Time:</b> {data.get('time')}", body_style))
    story.append(Paragraph(f"<b>Party Size:</b> {data.get('party_size')} guests", body_style))
    if data.get("notes"):
        story.append(Paragraph(f"<b>Special Notes:</b> {data.get('notes')}", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
