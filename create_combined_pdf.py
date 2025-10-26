#!/usr/bin/env python3
"""
Create a combined PDF with all documentation
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_combined_pdf():
    """Create a combined PDF with all documentation"""
    try:
        # Create document
        doc = SimpleDocTemplate("Mifumo_SMS_API_Complete_Documentation.pdf", pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center
        )
        
        heading1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50'),
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=10
        )
        
        elements = []
        
        # Title page
        elements.append(Paragraph("Mifumo SMS API", title_style))
        elements.append(Paragraph("Complete Integration Guide", title_style))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Secure SMS Messaging Integration for Tanzania", styles['Normal']))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Version 1.0", styles['Normal']))
        elements.append(Paragraph("October 2025", styles['Normal']))
        elements.append(PageBreak())
        
        # Table of Contents
        elements.append(Paragraph("Table of Contents", heading1_style))
        elements.append(Spacer(1, 20))
        
        toc_items = [
            "1. SMS API Endpoints",
            "2. Contacts API Endpoints", 
            "3. Segments API Endpoints",
            "4. Webhook Notifications",
            "5. API Key Management",
            "6. Error Codes",
            "7. Rate Limits",
            "8. Quick Reference Guide",
            "9. Support Information"
        ]
        
        for item in toc_items:
            elements.append(Paragraph(item, styles['Normal']))
            elements.append(Spacer(1, 8))
        
        elements.append(PageBreak())
        
        # Add content from main documentation
        with open('MIFUMO_SMS_API_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Main headings
            if line.startswith('## '):
                elements.append(Paragraph(line[3:], heading1_style))
                elements.append(Spacer(1, 12))
            
            # Sub headings
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], styles['Heading2']))
                elements.append(Spacer(1, 8))
            
            # Code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    elements.append(Paragraph(f'<font name="Courier">{code_text}</font>', styles['Code']))
                    elements.append(Spacer(1, 8))
            
            # Regular paragraphs
            else:
                if line.startswith('- '):
                    line = f"• {line[2:]}"
                elif line.startswith('**') and line.endswith('**'):
                    line = f"<b>{line[2:-2]}</b>"
                elif line.startswith('`') and line.endswith('`'):
                    line = f'<font name="Courier">{line[1:-1]}</font>'
                
                elements.append(Paragraph(line, styles['Normal']))
                elements.append(Spacer(1, 6))
            
            i += 1
        
        # Add page break before quick reference
        elements.append(PageBreak())
        elements.append(Paragraph("Quick Reference Guide", heading1_style))
        elements.append(Spacer(1, 20))
        
        # Add quick reference content
        with open('API_QUICK_REFERENCE.md', 'r', encoding='utf-8') as f:
            quick_content = f.read()
        
        lines = quick_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Main headings
            if line.startswith('## '):
                elements.append(Paragraph(line[3:], heading1_style))
                elements.append(Spacer(1, 12))
            
            # Sub headings
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], styles['Heading2']))
                elements.append(Spacer(1, 8))
            
            # Code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    elements.append(Paragraph(f'<font name="Courier">{code_text}</font>', styles['Code']))
                    elements.append(Spacer(1, 8))
            
            # Regular paragraphs
            else:
                if line.startswith('- '):
                    line = f"• {line[2:]}"
                elif line.startswith('**') and line.endswith('**'):
                    line = f"<b>{line[2:-2]}</b>"
                elif line.startswith('`') and line.endswith('`'):
                    line = f'<font name="Courier">{line[1:-1]}</font>'
                
                elements.append(Paragraph(line, styles['Normal']))
                elements.append(Spacer(1, 6))
            
            i += 1
        
        # Build PDF
        doc.build(elements)
        print("Combined PDF created successfully: Mifumo_SMS_API_Complete_Documentation.pdf")
        return True
        
    except Exception as e:
        print(f"Error creating combined PDF: {e}")
        return False

if __name__ == "__main__":
    success = create_combined_pdf()
    if success:
        file_size = os.path.getsize("Mifumo_SMS_API_Complete_Documentation.pdf")
        print(f"File size: {file_size:,} bytes")
    else:
        print("Failed to create combined PDF")

