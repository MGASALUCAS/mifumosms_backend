#!/usr/bin/env python3
"""
Start Server on Port 8081
========================

This script starts the server on port 8081 to avoid conflicts.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_html_file():
    """Serve the HTML file on port 8081"""
    print("Starting Server on Port 8081")
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
    
    # Use port 8081
    port = 8081
    
    try:
        with socketserver.TCPServer(("", port), HTMLHandler) as httpd:
            print(f"Server started on port {port}")
            print(f"URL: http://localhost:{port}/purchase_packages.html")
            print("Press Ctrl+C to stop")
            
            # Open browser
            try:
                webbrowser.open(f"http://localhost:{port}/purchase_packages.html")
                print("Browser opened!")
            except:
                print("Could not open browser automatically")
            
            # Start serving
            httpd.serve_forever()
                
    except OSError as e:
        print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    serve_html_file()
