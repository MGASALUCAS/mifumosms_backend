#!/usr/bin/env python3
"""
Start Final System
=================

This script starts both Django and the purchase page on port 8081.
"""

import subprocess
import sys
import time
import webbrowser
import requests
import os

def check_django():
    """Check if Django is running"""
    try:
        response = requests.get("http://localhost:8000/api/billing/sms/packages/", timeout=3)
        return response.status_code == 401
    except:
        return False

def start_django():
    """Start Django server"""
    if check_django():
        print("Django server is already running!")
        return True
    
    print("Starting Django server...")
    try:
        subprocess.Popen([
            sys.executable, 'manage.py', 'runserver'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Waiting for Django to start...")
        for i in range(10):
            time.sleep(1)
            if check_django():
                print("Django server started successfully!")
                return True
            print(f"Waiting... ({i+1}/10)")
        
        print("Django server failed to start")
        return False
    except Exception as e:
        print(f"Error starting Django: {e}")
        return False

def start_purchase_page():
    """Start purchase page server on port 8081"""
    print("Starting purchase page server on port 8081...")
    try:
        subprocess.Popen([
            sys.executable, 'start_on_8081.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Waiting for purchase page to start...")
        for i in range(5):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8081/purchase_packages.html", timeout=2)
                if response.status_code == 200 and "Mifumo SMS Packages" in response.text:
                    print("Purchase page server started successfully!")
                    return "http://localhost:8081/purchase_packages.html"
            except:
                pass
            print(f"Waiting... ({i+1}/5)")
        
        print("Purchase page server failed to start")
        return None
    except Exception as e:
        print(f"Error starting purchase page server: {e}")
        return None

def main():
    print("Starting Mifumo SMS System (Final)")
    print("=" * 50)
    
    # Start Django
    if not start_django():
        print("Failed to start Django server. Please run: python manage.py runserver")
        return
    
    # Start Purchase Page
    page_url = start_purchase_page()
    if not page_url:
        print("Failed to start purchase page server.")
        return
    
    print("\n" + "=" * 50)
    print("SYSTEM READY!")
    print("=" * 50)
    print(f"Django API: http://localhost:8000")
    print(f"Purchase Page: {page_url}")
    print()
    print("Opening purchase page...")
    
    # Open the purchase page
    try:
        webbrowser.open(page_url)
        print("Purchase page opened in browser!")
    except:
        print(f"Could not open browser automatically.")
        print(f"Please open: {page_url}")
    
    print("\nThe system is now ready to use!")
    print("The purchase page will automatically check if Django is running.")

if __name__ == '__main__':
    main()
