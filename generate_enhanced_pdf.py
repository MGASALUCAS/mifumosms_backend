#!/usr/bin/env python3
"""
Generate enhanced professional PDF documentation
"""

import os
import sys
from pathlib import Path

def install_requirements():
    """Install required packages for PDF generation"""
    try:
        import reportlab
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        print("Required packages already installed")
        return True
    except ImportError:
        print("Installing required packages...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
            print("Packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            return False

def create_enhanced_pdf():
    """Create enhanced professional PDF documentation"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics import renderPDF
        
        # Create document with custom margins
        doc = SimpleDocTemplate(
            "Mifumo_SMS_API_Professional_Documentation.pdf", 
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Enhanced custom styles
        title_style = ParagraphStyle(
            'EnhancedTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=40,
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'EnhancedSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading1_style = ParagraphStyle(
            'EnhancedH1',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            spaceBefore=25,
            textColor=colors.HexColor('#2b6cb0'),
            borderWidth=2,
            borderColor=colors.HexColor('#3182ce'),
            borderPadding=12,
            backColor=colors.HexColor('#ebf8ff'),
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'EnhancedH2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        )
        
        heading3_style = ParagraphStyle(
            'EnhancedH3',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#4a5568'),
            fontName='Helvetica-Bold'
        )
        
        code_style = ParagraphStyle(
            'EnhancedCode',
            parent=styles['Code'],
            fontSize=10,
            fontName='Courier',
            backColor=colors.HexColor('#1a202c'),
            textColor=colors.HexColor('#e2e8f0'),
            borderWidth=1,
            borderColor=colors.HexColor('#4a5568'),
            borderPadding=8,
            leftIndent=20,
            rightIndent=20
        )
        
        endpoint_style = ParagraphStyle(
            'Endpoint',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Courier-Bold',
            textColor=colors.HexColor('#2b6cb0'),
            backColor=colors.HexColor('#f7fafc'),
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8,
            leftIndent=10
        )
        
        method_style = ParagraphStyle(
            'Method',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            backColor=colors.HexColor('#38a169'),
            borderPadding=4,
            alignment=TA_CENTER
        )
        
        normal_style = ParagraphStyle(
            'EnhancedNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica'
        )
        
        elements = []
        
        # Title page with enhanced design
        elements.append(Spacer(1, 50))
        elements.append(Paragraph("Mifumo SMS API", title_style))
        elements.append(Paragraph("Integration Guide", subtitle_style))
        elements.append(Spacer(1, 30))
        
        # Add decorative line
        elements.append(Table([['']], colWidths=[6*inch], 
                             style=TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#3182ce'))])))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Secure SMS Messaging Integration for Tanzania", normal_style))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Version 1.0 | October 2025", normal_style))
        elements.append(PageBreak())
        
        # Table of Contents
        elements.append(Paragraph("Table of Contents", heading1_style))
        elements.append(Spacer(1, 20))
        
        toc_data = [
            ['1.', 'SMS API Endpoints', ''],
            ['', '  • Send SMS', '3'],
            ['', '  • Get Message Status', '4'],
            ['', '  • Get Delivery Reports', '5'],
            ['', '  • Get Account Balance', '6'],
            ['2.', 'Contacts API Endpoints', ''],
            ['', '  • Create Contact', '7'],
            ['', '  • Search Contacts', '8'],
            ['3.', 'Segments API Endpoints', '9'],
            ['4.', 'Webhook Notifications', '10'],
            ['5.', 'API Key Management', '11'],
            ['6.', 'Error Codes & Rate Limits', '12'],
            ['7.', 'Support Information', '13']
        ]
        
        toc_table = Table(toc_data, colWidths=[0.5*inch, 4*inch, 0.5*inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(toc_table)
        elements.append(PageBreak())
        
        # SMS API Section
        elements.append(Paragraph("SMS API Endpoints", heading1_style))
        elements.append(Spacer(1, 20))
        
        # Send SMS
        elements.append(Paragraph("Send SMS", heading2_style))
        
        # URL and Method
        url_method_data = [
            ['URL:', 'http://127.0.0.1:8001/api/integration/v1/sms/send/', 'Method:', 'POST']
        ]
        url_method_table = Table(url_method_data, colWidths=[0.8*inch, 4*inch, 0.8*inch, 1*inch])
        url_method_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (3, 0), (3, 0), colors.white),
            ('BACKGROUND', (3, 0), (3, 0), colors.HexColor('#38a169')),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(url_method_table)
        elements.append(Spacer(1, 15))
        
        # Authentication
        elements.append(Paragraph("Authentication", heading3_style))
        elements.append(Paragraph("Include your API key in the header:", normal_style))
        elements.append(Paragraph('<font name="Courier">Authorization: Bearer YOUR_API_KEY</font>', code_style))
        elements.append(Paragraph("<b>Note:</b> Replace YOUR_API_KEY with the key provided by Mifumo SMS.", normal_style))
        elements.append(Spacer(1, 15))
        
        # Request Body
        elements.append(Paragraph("Request Body", heading3_style))
        elements.append(Paragraph("Submit the following JSON payload:", normal_style))
        
        json_payload = '''{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789", "+255987654321"],
  "sender_id": "MIFUMO",
  "schedule_time": "2024-01-01T10:00:00Z"
}'''
        elements.append(Paragraph(f'<font name="Courier">{json_payload}</font>', code_style))
        elements.append(Spacer(1, 15))
        
        # Parameter Descriptions
        elements.append(Paragraph("Parameter Descriptions", heading3_style))
        
        param_data = [
            ['Parameter', 'Type', 'Required', 'Description'],
            ['message', 'string', '✓', 'SMS text content (max 160 characters)'],
            ['recipients', 'array', '✓', 'List of phone numbers in E.164 format'],
            ['sender_id', 'string', '✗', 'Custom sender ID (default: "MIFUMO")'],
            ['schedule_time', 'string', '✗', 'ISO 8601 datetime for scheduled sending']
        ]
        
        param_table = Table(param_data, colWidths=[1.2*inch, 0.8*inch, 0.6*inch, 3.4*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#38a169')),
        ]))
        elements.append(param_table)
        elements.append(Spacer(1, 20))
        
        # Sample cURL Request
        elements.append(Paragraph("Sample cURL Request", heading3_style))
        
        curl_example = '''curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{
    "message": "Hello from Mifumo SMS!",
    "recipients": ["+255123456789"],
    "sender_id": "MIFUMO"
  }' '''
        elements.append(Paragraph(f'<font name="Courier">{curl_example}</font>', code_style))
        elements.append(Spacer(1, 20))
        
        # Response Examples
        elements.append(Paragraph("Response Examples", heading3_style))
        
        # Successful Response
        elements.append(Paragraph("Successful Response", heading3_style))
        success_response = '''{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "msg_123456789",
    "recipients": ["+255123456789"],
    "status": "sent",
    "cost": 10.0,
    "currency": "TZS"
  },
  "error_code": null,
  "details": null
}'''
        elements.append(Paragraph(f'<font name="Courier">{success_response}</font>', code_style))
        elements.append(Spacer(1, 15))
        
        # Error Response
        elements.append(Paragraph("Error Response", heading3_style))
        error_response = '''{
  "success": false,
  "message": "Invalid API Key or request payload",
  "data": null,
  "error_code": "INVALID_CREDENTIALS",
  "details": "The provided API key is invalid or expired"
}'''
        elements.append(Paragraph(f'<font name="Courier">{error_response}</font>', code_style))
        elements.append(PageBreak())
        
        # Continue with other endpoints...
        elements.append(Paragraph("Get Message Status", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/sms/status/{message_id}/", endpoint_style))
        elements.append(Paragraph("Method: GET", method_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Get Delivery Reports", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/", endpoint_style))
        elements.append(Paragraph("Method: GET", method_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Get Account Balance", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/sms/balance/", endpoint_style))
        elements.append(Paragraph("Method: GET", method_style))
        elements.append(PageBreak())
        
        # Contacts API
        elements.append(Paragraph("Contacts API Endpoints", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Create Contact", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/contacts/create/", endpoint_style))
        elements.append(Paragraph("Method: POST", method_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Search Contacts", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/contacts/search/", endpoint_style))
        elements.append(Paragraph("Method: GET", method_style))
        elements.append(PageBreak())
        
        # Segments API
        elements.append(Paragraph("Segments API Endpoints", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Create Segment", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/v1/contacts/segments/create/", endpoint_style))
        elements.append(Paragraph("Method: POST", method_style))
        elements.append(PageBreak())
        
        # Webhooks
        elements.append(Paragraph("Webhook Notifications", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Mifumo SMS can send automatic notifications to your server when SMS status changes.", normal_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Webhook Setup", heading2_style))
        elements.append(Paragraph("Include the webhook_url parameter in your SMS request:", normal_style))
        
        webhook_example = '''{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789"],
  "sender_id": "MIFUMO",
  "webhook_url": "https://your-domain.com/sms-webhook"
}'''
        elements.append(Paragraph(f'<font name="Courier">{webhook_example}</font>', code_style))
        elements.append(PageBreak())
        
        # API Key Management
        elements.append(Paragraph("API Key Management", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Dashboard Access", heading2_style))
        elements.append(Paragraph("URL: http://127.0.0.1:8001/api/integration/dashboard/", endpoint_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Access your API dashboard to:", normal_style))
        elements.append(Paragraph("• Generate new API keys", normal_style))
        elements.append(Paragraph("• View usage statistics", normal_style))
        elements.append(Paragraph("• Manage webhooks", normal_style))
        elements.append(Paragraph("• Monitor account activity", normal_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("API Key Permissions", heading2_style))
        elements.append(Paragraph("• read: View data and reports", normal_style))
        elements.append(Paragraph("• write: Send SMS and manage contacts", normal_style))
        elements.append(Paragraph("• admin: Full account management", normal_style))
        elements.append(PageBreak())
        
        # Error Codes
        elements.append(Paragraph("Error Codes", heading1_style))
        elements.append(Spacer(1, 20))
        
        error_data = [
            ['Code', 'Description'],
            ['INVALID_CREDENTIALS', 'Invalid or expired API key'],
            ['INVALID_PHONE', 'Invalid phone number format'],
            ['INSUFFICIENT_BALANCE', 'Account balance too low'],
            ['RATE_LIMIT_EXCEEDED', 'Too many requests'],
            ['INVALID_SENDER_ID', 'Sender ID not approved'],
            ['MESSAGE_TOO_LONG', 'SMS exceeds character limit']
        ]
        
        error_table = Table(error_data, colWidths=[2*inch, 4*inch])
        error_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e53e3e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef5e7')),
        ]))
        elements.append(error_table)
        elements.append(Spacer(1, 20))
        
        # Rate Limits
        elements.append(Paragraph("Rate Limits", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("• SMS Sending: 100 messages per minute", normal_style))
        elements.append(Paragraph("• API Calls: 1000 requests per hour", normal_style))
        elements.append(Paragraph("• Contact Management: 500 operations per hour", normal_style))
        elements.append(PageBreak())
        
        # Support
        elements.append(Paragraph("Support Information", heading1_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("For assistance, contact:", normal_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("• Email: support@mifumosms.com", normal_style))
        elements.append(Paragraph("• Website: http://127.0.0.1:8001", normal_style))
        elements.append(Paragraph("• Documentation: http://127.0.0.1:8001/api/integration/documentation/", normal_style))
        elements.append(Spacer(1, 30))
        
        # Footer
        elements.append(Table([['']], colWidths=[6*inch], 
                             style=TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#3182ce'))])))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Mifumo SMS Team", heading2_style))
        elements.append(Paragraph("<i>Simplifying SMS Communication in Tanzania</i>", normal_style))
        
        # Build PDF
        doc.build(elements)
        print("Enhanced PDF created successfully: Mifumo_SMS_API_Professional_Documentation.pdf")
        return True
        
    except Exception as e:
        print(f"Error creating enhanced PDF: {e}")
        return False

def main():
    """Main function to generate enhanced PDF documentation"""
    print("Generating Enhanced Professional PDF Documentation")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Exiting.")
        return False
    
    # Create enhanced PDF
    if create_enhanced_pdf():
        file_size = os.path.getsize("Mifumo_SMS_API_Professional_Documentation.pdf")
        print(f"File size: {file_size:,} bytes")
        print("Enhanced PDF generated successfully!")
        return True
    else:
        print("Failed to create enhanced PDF")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

