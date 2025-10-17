#!/usr/bin/env python3
"""
Simple HTTP Server for Purchase Page
===================================

This script serves the purchase_packages.html file locally.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def serve_purchase_page():
    """Serve the purchase page locally"""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    html_file = script_dir / "purchase_packages.html"
    
    if not html_file.exists():
        print("Error: purchase_packages.html not found!")
        print(f"Expected location: {html_file}")
        return
    
    # Change to the script directory
    os.chdir(script_dir)
    print(f"Serving from directory: {os.getcwd()}")
    print(f"HTML file exists: {html_file.exists()}")
    
    # Set up the server - try different ports if 8080 is busy
    PORTS = [8080, 8081, 8082, 8083, 8084]
    PORT = None
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow API calls
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            super().end_headers()
        
        def do_GET(self):
            # Handle root path and purchase_packages.html
            if self.path == '/' or self.path == '/purchase_packages.html':
                self.path = '/purchase_packages.html'
            super().do_GET()
    
    # Try to find an available port
    for port in PORTS:
        try:
            with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
                PORT = port
                print("Purchase Page Server Started!")
                print("=" * 50)
                print(f"Purchase Page: http://localhost:{PORT}/purchase_packages.html")
                print(f"Direct Link: http://127.0.0.1:{PORT}/purchase_packages.html")
                print()
                print("Features:")
                print("   - Browse SMS packages")
                print("   - Select package")
                print("   - Fill payment details")
                print("   - Auto-suggest mobile money provider")
                print("   - Initiate payment with ZenoPay")
                print("   - Real-time payment status")
                print()
                print("Press Ctrl+C to stop the server")
                print("=" * 50)
                
                # Try to open the browser automatically
                try:
                    webbrowser.open(f"http://localhost:{PORT}/purchase_packages.html")
                    print("Opening browser automatically...")
                except:
                    print("Could not open browser automatically. Please open the link manually.")
                
                # Start the server
                httpd.serve_forever()
                break
                
        except OSError as e:
            if e.errno == 10048:  # Address already in use (Windows)
                print(f"Port {port} is busy, trying next port...")
                continue
            else:
                print(f"Error starting server on port {port}: {e}")
                break
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            break
        except Exception as e:
            print(f"Unexpected error on port {port}: {e}")
            break
    
    if PORT is None:
        print("ERROR: Could not find an available port!")
        print("Please close other applications or restart your computer.")

def main():
    print("Mifumo SMS Purchase Page Server")
    print("=" * 50)
    print("This will serve the purchase_packages.html file locally")
    print()
    
    serve_purchase_page()

if __name__ == '__main__':
    main()
