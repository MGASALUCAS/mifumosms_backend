#!/usr/bin/env python3
"""
Create PDF Documentation
Converts the markdown summary to PDF format
"""

import os
import sys
import subprocess
from datetime import datetime

def create_pdf_documentation():
    """Create PDF documentation from markdown"""
    print("📄 Creating PDF Documentation...")
    print("=" * 50)
    
    try:
        # Check if required packages are installed
        try:
            import markdown
            import pdfkit
            print("✅ Required packages found")
        except ImportError:
            print("📦 Installing required packages...")
            subprocess.run([sys.executable, "-m", "pip", "install", "markdown", "pdfkit", "wkhtmltopdf"], check=True)
            import markdown
            import pdfkit
        
        # Read the markdown file
        with open('MIFUMO_SMS_BACKEND_SETUP_SUMMARY.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # Add CSS styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mifumo SMS Backend - Setup Summary</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    font-size: 2.5em;
                    margin-bottom: 30px;
                }}
                h2 {{
                    color: #34495e;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 5px;
                    margin-top: 30px;
                    font-size: 1.8em;
                }}
                h3 {{
                    color: #2980b9;
                    margin-top: 25px;
                    font-size: 1.4em;
                }}
                h4 {{
                    color: #8e44ad;
                    margin-top: 20px;
                    font-size: 1.2em;
                }}
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                ul, ol {{
                    margin-bottom: 15px;
                    padding-left: 30px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background-color: #f8f8f8;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                    overflow-x: auto;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .status-success {{
                    color: #27ae60;
                    font-weight: bold;
                }}
                .status-warning {{
                    color: #f39c12;
                    font-weight: bold;
                }}
                .status-error {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                    margin: 15px 0;
                }}
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 2px solid #ecf0f1;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
                @media print {{
                    body {{
                        background: white;
                        margin: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        padding: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_content}
                <div class="footer">
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p>Mifumo SMS Backend System - Complete Setup Documentation</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML file
        with open('MIFUMO_SMS_BACKEND_SETUP_SUMMARY.html', 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        print("✅ HTML file created: MIFUMO_SMS_BACKEND_SETUP_SUMMARY.html")
        
        # Convert to PDF
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            pdfkit.from_string(styled_html, 'MIFUMO_SMS_BACKEND_SETUP_SUMMARY.pdf', options=options)
            print("✅ PDF file created: MIFUMO_SMS_BACKEND_SETUP_SUMMARY.pdf")
            
        except Exception as e:
            print(f"⚠️  PDF creation failed: {e}")
            print("📄 HTML file is available for manual PDF conversion")
            print("   You can open MIFUMO_SMS_BACKEND_SETUP_SUMMARY.html in a browser and print to PDF")
        
        print("\n📊 Documentation Summary:")
        print(f"   📄 HTML: MIFUMO_SMS_BACKEND_SETUP_SUMMARY.html")
        print(f"   📄 PDF: MIFUMO_SMS_BACKEND_SETUP_SUMMARY.pdf")
        print(f"   📄 Markdown: MIFUMO_SMS_BACKEND_SETUP_SUMMARY.md")
        
        print(f"\n✅ Documentation creation completed!")
        
    except Exception as e:
        print(f"❌ Error creating documentation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_pdf_documentation()
