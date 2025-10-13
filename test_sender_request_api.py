#!/usr/bin/env python
"""
Simple test script to verify sender name request API functionality.
Run this after starting the development server.
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
SENDER_REQUEST_URL = f"{BASE_URL}/messaging/sender-requests/"

# Test credentials (adjust as needed)
TEST_EMAIL = "admin@example.com"
TEST_PASSWORD = "admin123"

def test_sender_request_api():
    """Test the sender name request API endpoints."""

    print("🧪 Testing Sender Name Request API")
    print("=" * 50)

    # Step 1: Login to get JWT token
    print("1. Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    try:
        login_response = requests.post(AUTH_URL, json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')
            if not access_token:
                print("❌ No access token received")
                return
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return

    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 2: Test statistics endpoint
    print("\n2. Testing statistics endpoint...")
    try:
        stats_response = requests.get(f"{SENDER_REQUEST_URL}stats/", headers=headers)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Statistics retrieved successfully")
            print(f"   Total requests: {stats_data.get('data', {}).get('total_requests', 0)}")
        else:
            print(f"❌ Statistics failed: {stats_response.status_code}")
            print(stats_response.text)
    except Exception as e:
        print(f"❌ Statistics error: {str(e)}")

    # Step 3: Test list endpoint
    print("\n3. Testing list endpoint...")
    try:
        list_response = requests.get(f"{SENDER_REQUEST_URL}", headers=headers)
        if list_response.status_code == 200:
            list_data = list_response.json()
            print("✅ List retrieved successfully")
            print(f"   Found {len(list_data.get('data', {}).get('results', []))} requests")
        else:
            print(f"❌ List failed: {list_response.status_code}")
            print(list_response.text)
    except Exception as e:
        print(f"❌ List error: {str(e)}")

    # Step 4: Test form submission (without files)
    print("\n4. Testing form submission...")
    form_data = {
        "sender_name": "TESTCOMPANY",
        "use_case": "This is a test sender name request for API testing purposes. We will use this for customer notifications and marketing campaigns."
    }

    try:
        submit_response = requests.post(f"{SENDER_REQUEST_URL}submit/", json=form_data, headers=headers)
        if submit_response.status_code == 201:
            submit_data = submit_response.json()
            print("✅ Form submission successful")
            request_id = submit_data.get('data', {}).get('id')
            print(f"   Request ID: {request_id}")

            # Step 5: Test detail endpoint
            if request_id:
                print(f"\n5. Testing detail endpoint for request {request_id}...")
                detail_response = requests.get(f"{SENDER_REQUEST_URL}{request_id}/", headers=headers)
                if detail_response.status_code == 200:
                    print("✅ Detail retrieved successfully")
                else:
                    print(f"❌ Detail failed: {detail_response.status_code}")
                    print(detail_response.text)
        else:
            print(f"❌ Form submission failed: {submit_response.status_code}")
            print(submit_response.text)
    except Exception as e:
        print(f"❌ Form submission error: {str(e)}")

    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_sender_request_api()
