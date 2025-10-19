#!/usr/bin/env python
"""
Test production endpoint
"""
import requests
import json

def test_production_endpoint():
    """Test the production sender-requests endpoint"""
    
    # Test without authentication (should return 401)
    url = "http://104.131.116.55/api/messaging/sender-requests/?page=1&page_size=10"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 404:
            print("❌ 404 Not Found - The endpoint doesn't exist on production")
            print("This means the production server doesn't have the updated code")
        elif response.status_code == 401:
            print("✅ 401 Unauthorized - The endpoint exists but requires authentication")
            print("This means the production server has the updated code")
        elif response.status_code == 200:
            print("✅ 200 OK - The endpoint works")
            data = response.json()
            print(f"Response data: {data}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_production_endpoint()
