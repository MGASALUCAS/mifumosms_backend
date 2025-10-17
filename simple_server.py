#!/usr/bin/env python3
"""
Simple File Server
=================

This script serves the purchase_packages.html file directly.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_html_file():
    """Serve the HTML file directly"""
    print("Simple HTML File Server")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    html_file = current_dir / "purchase_packages.html"
    
    print(f"Current directory: {current_dir}")
    print(f"HTML file path: {html_file}")
    print(f"HTML file exists: {html_file.exists()}")
    
    if not html_file.exists():
        print("ERROR: purchase_packages.html not found!")
        return
    
    # Change to the directory containing the HTML file
    os.chdir(current_dir)
    print(f"Changed to directory: {os.getcwd()}")
    
    class HTMLHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            super().end_headers()
        
        def do_GET(self):
            # Always serve the HTML file
            if self.path == '/' or self.path == '/purchase_packages.html':
                self.path = '/purchase_packages.html'
                print(f"Serving: {self.path}")
            super().do_GET()
    
    # Try different ports
    ports = [8080, 8081, 8082, 8083, 8084]
    
    for port in ports:
        try:
            with socketserver.TCPServer(("", port), HTMLHandler) as httpd:
                print(f"Server started on port {port}")
                print(f"URL: http://localhost:{port}/purchase_packages.html")
                print("Press Ctrl+C to stop")
                
                # Open browser
                try:
                    webbrowser.open(f"http://localhost:{port}/purchase_packages.html")
                except:
                    pass
                
                # Start serving
                httpd.serve_forever()
                break
                
        except OSError as e:
            if e.errno == 10048:  # Port already in use
                print(f"Port {port} is busy, trying next...")
                continue
            else:
                print(f"Error on port {port}: {e}")
                break
        except KeyboardInterrupt:
            print("\nServer stopped")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == '__main__':
    serve_html_file()
