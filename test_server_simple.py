#!/usr/bin/env python3
"""
Simple server test
"""

import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_server():
    print("🧪 Testing Django server on port 8001...")
    
    # Test basic endpoints
    endpoints = [
        'http://127.0.0.1:8001/api/health/',
        'http://127.0.0.1:8001/api/auth/register/',
        'http://127.0.0.1:8001/swagger/',
    ]
    
    for url in endpoints:
        print(f'\nTesting: {url}')
        try:
            response = requests.get(url, timeout=5, verify=False)
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print('✅ Server is responding!')
            else:
                print(f'Response: {response.text[:100]}')
        except Exception as e:
            print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_server()
