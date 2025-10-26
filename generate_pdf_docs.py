#!/usr/bin/env python3
"""
Generate PDF documentation from markdown files
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages for PDF generation"""
    try:
        import markdown
        import pdfkit
        print("Required packages already installed")
        return True
    except ImportError:
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "pdfkit", "wkhtmltopdf"])
            print("Packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            return False

def markdown_to_html(markdown_file):
    """Convert markdown file to HTML"""
    try:
        import markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code', 'toc'])
        
        # Add CSS styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mifumo SMS API Documentation</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #fff;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-top: 40px;
                }}
                h2 {{
                    color: #34495e;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 8px;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #7f8c8d;
                    margin-top: 25px;
                }}
                h4 {{
                    color: #95a5a6;
                    margin-top: 20px;
                }}
                code {{
                    background: #f8f9fa;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    margin: 15px 0;
                }}
                pre code {{
                    background: none;
                    padding: 0;
                    color: inherit;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background: #3498db;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background: #f8f9fa;
                }}
                .endpoint {{
                    background: #e8f5e8;
                    padding: 10px;
                    border-left: 4px solid #27ae60;
                    margin: 10px 0;
                }}
                .method {{
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 0.8em;
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .url {{
                    font-family: monospace;
                    background: #f8f9fa;
                    padding: 4px 8px;
                    border-radius: 3px;
                }}
                .required {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .optional {{
                    color: #95a5a6;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                    padding: 10px 20px;
                    background: #f8f9fa;
                }}
                .toc {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .toc ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                .toc li {{
                    margin: 5px 0;
                }}
                .toc a {{
                    text-decoration: none;
                    color: #3498db;
                }}
                .toc a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        return styled_html
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return None

def html_to_pdf(html_content, output_file):
    """Convert HTML to PDF"""
    try:
        import pdfkit
        
        # Configure options for better PDF output
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'disable-smart-shrinking': None,
        }
        
        # Convert HTML to PDF
        pdfkit.from_string(html_content, output_file, options=options)
        print(f"PDF generated successfully: {output_file}")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        print("Make sure wkhtmltopdf is installed on your system")
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
        
        # Convert markdown to HTML
        print("  Converting markdown to HTML...")
        html_content = markdown_to_html(markdown_file)
        if not html_content:
            print(f"Failed to convert {markdown_file}")
            continue
        
        # Convert HTML to PDF
        print("  Converting HTML to PDF...")
        if html_to_pdf(html_content, pdf_file):
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
