#!/usr/bin/env python
"""
Test script for running server endpoints
"""
import requests
import json

def test_running_server():
    """Test endpoints on the running server"""
    
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("TESTING RUNNING SERVER ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Contacts endpoint
    print("\n" + "=" * 40)
    print("TEST 1: CONTACTS ENDPOINT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/messaging/contacts/")
        print(f"GET /api/messaging/contacts/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint exists and requires authentication")
        elif response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Found {len(data)} contacts")
        else:
            print(f"ERROR: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 2: Sender Requests endpoint
    print("\n" + "=" * 40)
    print("TEST 2: SENDER REQUESTS ENDPOINT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/?page=1&page_size=10")
        print(f"GET /api/messaging/sender-requests/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint exists and requires authentication")
        elif response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Found {len(data)} sender requests")
        else:
            print(f"ERROR: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 3: Sender IDs endpoint
    print("\n" + "=" * 40)
    print("TEST 3: SENDER IDS ENDPOINT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-ids/")
        print(f"GET /api/messaging/sender-ids/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint exists and requires authentication")
        elif response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Found {len(data.get('data', []))} sender IDs")
        else:
            print(f"ERROR: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 4: SMS Send endpoint
    print("\n" + "=" * 40)
    print("TEST 4: SMS SEND ENDPOINT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/messaging/sms/send/")
        print(f"GET /api/messaging/sms/send/ - Status: {response.status_code}")
        
        if response.status_code == 405:
            print("SUCCESS: Endpoint exists (Method Not Allowed for GET)")
        elif response.status_code == 401:
            print("SUCCESS: Endpoint exists and requires authentication")
        else:
            print(f"ERROR: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 5: Admin interface
    print("\n" + "=" * 40)
    print("TEST 5: ADMIN INTERFACE")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/admin/billing/smsbalance/")
        print(f"GET /admin/billing/smsbalance/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Admin SMSBalance page loads")
        elif response.status_code == 302:
            print("SUCCESS: Admin page redirects to login (expected)")
        else:
            print(f"ERROR: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_running_server()
