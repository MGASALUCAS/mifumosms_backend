#!/usr/bin/env python3
"""
Start Both Servers
=================

This script starts both Django and the purchase page servers.
"""

import subprocess
import sys
import time
import webbrowser
import os

def start_django():
    """Start Django server"""
    print("Starting Django server...")
    try:
        # Start Django in background
        django_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Django server started on http://localhost:8000")
        return django_process
    except Exception as e:
        print(f"Error starting Django: {e}")
        return None

def start_purchase_page():
    """Start purchase page server"""
    print("Starting purchase page server...")
    try:
        # Start purchase page server in background
        page_process = subprocess.Popen([
            sys.executable, 'serve_purchase_page.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Purchase page server started on http://localhost:8080")
        return page_process
    except Exception as e:
        print(f"Error starting purchase page server: {e}")
        return None

def main():
    print("Starting Mifumo SMS Servers")
    print("=" * 50)
    
    # Start Django
    django_process = start_django()
    if not django_process:
        print("Failed to start Django server")
        return
    
    # Wait a moment for Django to start
    print("Waiting for Django to start...")
    time.sleep(3)
    
    # Start purchase page server
    page_process = start_purchase_page()
    if not page_process:
        print("Failed to start purchase page server")
        return
    
    # Wait a moment for purchase page to start
    print("Waiting for purchase page to start...")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("SERVERS STARTED SUCCESSFULLY!")
    print("=" * 50)
    print("Django API: http://localhost:8000")
    print("Purchase Page: http://localhost:8080/purchase_packages.html")
    print()
    print("Opening purchase page in browser...")
    
    # Open the purchase page
    try:
        webbrowser.open("http://localhost:8080/purchase_packages.html")
    except:
        print("Could not open browser automatically")
        print("Please open: http://localhost:8080/purchase_packages.html")
    
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        if django_process:
            django_process.terminate()
        if page_process:
            page_process.terminate()
        print("Servers stopped")

if __name__ == '__main__':
    main()
