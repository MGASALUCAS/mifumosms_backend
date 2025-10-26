#!/usr/bin/env python3
"""
Generate PDF documentation using reportlab (no external dependencies)
"""

import os
import sys
from pathlib import Path

def install_requirements():
    """Install required packages for PDF generation"""
    try:
        import reportlab
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
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

def parse_markdown_to_elements(markdown_file):
    """Parse markdown file and convert to reportlab elements"""
    try:
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
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
        
        heading2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#34495e')
        )
        
        heading3_style = ParagraphStyle(
            'CustomH3',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#7f8c8d')
        )
        
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontSize=9,
            fontName='Courier',
            backColor=colors.HexColor('#f8f9fa'),
            borderWidth=1,
            borderColor=colors.HexColor('#dee2e6'),
            borderPadding=5
        )
        
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Title
            if line.startswith('# Mifumo SMS API'):
                elements.append(Paragraph(line[2:], title_style))
                elements.append(Spacer(1, 20))
            
            # Main headings
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], heading1_style))
                elements.append(Spacer(1, 12))
            
            # Sub headings
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], heading2_style))
                elements.append(Spacer(1, 8))
            
            # Sub sub headings
            elif line.startswith('#### '):
                elements.append(Paragraph(line[5:], heading3_style))
                elements.append(Spacer(1, 6))
            
            # Code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    elements.append(Paragraph(f'<font name="Courier">{code_text}</font>', code_style))
                    elements.append(Spacer(1, 8))
            
            # Tables
            elif '|' in line and '---' in lines[i+1] if i+1 < len(lines) else False:
                table_data = []
                # Header row
                header_cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                table_data.append(header_cells)
                
                # Skip separator row
                i += 1
                
                # Data rows
                i += 1
                while i < len(lines) and '|' in lines[i]:
                    row_cells = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                    if row_cells:
                        table_data.append(row_cells)
                    i += 1
                
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                continue
            
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
        
        return elements
    except Exception as e:
        print(f"Error parsing markdown: {e}")
        return []

def create_pdf(elements, output_file):
    """Create PDF from elements"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        doc.build(elements)
        print(f"PDF created successfully: {output_file}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def main():
    """Main function to generate PDF documentation"""
    print("Generating PDF Documentation for Mifumo SMS API")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Exiting.")
        return False
    
    # Files to convert
    files_to_convert = [
        {
            'markdown': 'MIFUMO_SMS_API_DOCUMENTATION.md',
            'pdf': 'Mifumo_SMS_API_Documentation.pdf'
        },
        {
            'markdown': 'API_QUICK_REFERENCE.md',
            'pdf': 'Mifumo_SMS_API_Quick_Reference.pdf'
        }
    ]
    
    success_count = 0
    
    for file_info in files_to_convert:
        markdown_file = file_info['markdown']
        pdf_file = file_info['pdf']
        
        print(f"\nProcessing: {markdown_file}")
        
        # Check if markdown file exists
        if not os.path.exists(markdown_file):
            print(f"File not found: {markdown_file}")
            continue
        
        # Parse markdown to elements
        print("  Converting markdown to PDF elements...")
        elements = parse_markdown_to_elements(markdown_file)
        if not elements:
            print(f"Failed to parse {markdown_file}")
            continue
        
        # Create PDF
        print("  Creating PDF...")
        if create_pdf(elements, pdf_file):
            success_count += 1
            print(f"Successfully created: {pdf_file}")
        else:
            print(f"Failed to create PDF for {markdown_file}")
    
    print("\n" + "=" * 60)
    print(f"Summary: {success_count}/{len(files_to_convert)} PDFs generated successfully")
    
    if success_count > 0:
        print("\nGenerated PDF files:")
        for file_info in files_to_convert:
            if os.path.exists(file_info['pdf']):
                file_size = os.path.getsize(file_info['pdf'])
                print(f"  • {file_info['pdf']} ({file_size:,} bytes)")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
