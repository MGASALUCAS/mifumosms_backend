#!/usr/bin/env python3
"""
Refresh Purchase Page
===================

This script helps refresh the purchase page and clear cache.
"""

import webbrowser
import time

def refresh_page():
    """Open the purchase page with cache busting"""
    print("Refreshing Purchase Page")
    print("=" * 50)
    
    # Add cache busting parameter
    cache_buster = int(time.time())
    url = f"http://localhost:8080/purchase_packages.html?v={cache_buster}"
    
    print(f"Opening: {url}")
    print()
    print("This will open the page with cache busting to ensure you get the latest version.")
    print()
    print("If the page still shows 'Loading packages...':")
    print("1. Press Ctrl+F5 to force refresh")
    print("2. Open browser developer tools (F12)")
    print("3. Check the Console tab for error messages")
    print("4. Check the Network tab for failed requests")
    print()
    print("The page should now work correctly with:")
    print("- Fixed phone number formatting (06 prefix)")
    print("- Corrected ZenoPay API implementation")
    print("- Better error handling and logging")
    print("- Cache busting to prevent 304 responses")
    
    try:
        webbrowser.open(url)
        print("\nPage opened in browser!")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please manually open: {url}")

def main():
    refresh_page()

if __name__ == '__main__':
    main()
