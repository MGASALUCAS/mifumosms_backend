#!/usr/bin/env python3
"""
Test script to verify frontend API endpoints that are failing.
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

def test_login():
    """Test login to get a valid token."""
    print("🔐 Testing login...")
    
    login_url = f"{BASE_URL}/api/auth/login/"
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'tokens' in data and 'access' in data['tokens']:
                token = data['tokens']['access']
                print(f"✅ Login successful, token: {token[:20]}...")
                return token
            else:
                print(f"❌ Login failed: {data}")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_endpoint(url, token, method="GET", data=None):
    """Test a specific endpoint."""
    print(f"\n🧪 Testing: {method} {url}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ Success: {json_data.get('success', 'Unknown')}")
                return True
            except:
                print(f"✅ Success (non-JSON response)")
                return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Frontend API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test the failing endpoints
    endpoints = [
        {
            "url": f"{BASE_URL}/api/auth/settings/profile/",
            "method": "GET",
            "description": "User Profile Settings (Correct URL)"
        },
        {
            "url": f"{BASE_URL}/api/accounts/settings/profile/",
            "method": "GET",
            "description": "User Profile Settings (Wrong URL - Frontend Issue)"
        },
        {
            "url": f"{BASE_URL}/api/messaging/dashboard/overview/",
            "method": "GET", 
            "description": "Dashboard Overview"
        },
        {
            "url": f"{BASE_URL}/api/messaging/dashboard/metrics/",
            "method": "GET",
            "description": "Dashboard Metrics"
        },
        {
            "url": f"{BASE_URL}/api/messaging/sender-requests/stats/",
            "method": "GET",
            "description": "Sender Requests Stats"
        }
    ]
    
    results = []
    for endpoint in endpoints:
        print(f"\n{'='*60}")
        print(f"Testing: {endpoint['description']}")
        print(f"URL: {endpoint['url']}")
        success = test_endpoint(endpoint['url'], token, endpoint['method'])
        results.append({
            "endpoint": endpoint['description'],
            "url": endpoint['url'],
            "success": success
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {result['endpoint']}")
        print(f"    URL: {result['url']}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\nResults: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    main()