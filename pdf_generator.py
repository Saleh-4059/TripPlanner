# pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os
from config import Config

def generate_pdf(trip_plan, filename=None):
    """Generate PDF trip plan"""
    
    # Ensure directory exists
    Config.ensure_directories()
    
    # Create filename
    if not filename:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = trip_plan['trip_info']['destination_code'][:10]
        filename = f"trip_plan_{dest}_{timestamp}.pdf"
    
    filepath = os.path.join(Config.PDF_OUTPUT_DIR, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"✈️ Trip Plan: {trip_plan['trip_info']['destination']}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Trip Information
    story.append(Paragraph("📍 Trip Information", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    trip_info = trip_plan['trip_info']
    info_data = [
        ["From:", f"{trip_info['origin']} ({trip_info['origin_code']})"],
        ["To:", f"{trip_info['destination']} ({trip_info['destination_code']})"],
        ["Departure:", trip_info['departure_date']],
        ["Return:", trip_info.get('return_date', 'One-way')],
        ["Travelers:", str(trip_info['travelers'])],
        ["Budget:", trip_info['budget'].title()]
    ]
    
    info_table = Table(info_data, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Flights
    if trip_plan['flights']:
        story.append(Paragraph("✈️ Flight Options", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if trip_plan['flights'][0].get('is_sample'):
            story.append(Paragraph("<i>Sample flight data shown</i>", styles['Italic']))
            story.append(Spacer(1, 5))
        
        flight_data = [["Airline", "Flight", "Departure", "Arrival", "Price"]]
        
        for flight in trip_plan['flights'][:3]:
            flight_data.append([
                flight['airline'],
                flight['flight_number'],
                flight.get('departure_time_display', flight['departure_time'])[:16],
                flight.get('arrival_time_display', flight['arrival_time'])[:16],
                f"${flight['price']}"
            ])
        
        flight_table = Table(flight_data, colWidths=[80, 60, 80, 80, 60])
        flight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6FA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8EEF4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(flight_table)
        story.append(Spacer(1, 20))
    
    # Attractions
    if trip_plan['attractions']:
        story.append(Paragraph("🏛️ Recommended Attractions", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for attraction in trip_plan['attractions']:
            story.append(Paragraph(f"• {attraction}", styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    # Packing List
    if trip_plan['packing_list']:
        story.append(Paragraph("🧳 Packing List", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for category, items in trip_plan['packing_list'].items():
            story.append(Paragraph(f"<b>{category.title()}:</b>", styles['Normal']))
            for item in items:
                story.append(Paragraph(f"   ✓ {item}", styles['Normal']))
            story.append(Spacer(1, 5))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated on: {trip_plan['created_at']}", styles['Normal']))
    story.append(Paragraph("Trip Planner Assistant", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated: {filepath}")
    return filename