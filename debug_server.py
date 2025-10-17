#!/usr/bin/env python3
"""
Debug Server
===========

This script debugs what the server is actually serving.
"""

import requests

def debug_server():
    """Debug what the server is serving"""
    print("Debugging Server Response")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8080/purchase_packages.html", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content Length: {len(response.text)}")
        print()
        print("First 500 characters of response:")
        print("-" * 50)
        print(response.text[:500])
        print("-" * 50)
        print()
        print("Last 200 characters of response:")
        print("-" * 50)
        print(response.text[-200:])
        print("-" * 50)
        
        # Check if it's a directory listing
        if "Directory listing for" in response.text:
            print("ISSUE: Server is showing directory listing instead of HTML file!")
        elif "Mifumo SMS Packages" in response.text:
            print("SUCCESS: HTML file is being served correctly!")
        else:
            print("ISSUE: Unknown content being served")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_server()
