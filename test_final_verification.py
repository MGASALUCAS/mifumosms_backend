#!/usr/bin/env python
"""
Final verification test with correct sender name length.
"""
import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
SUBMIT_URL = f"{BASE_URL}/messaging/sender-requests/submit/"

def test_final_verification():
    """Final test with correct sender name length."""
    print("🎯 Final Verification Test")
    print("=" * 40)

    # Login
    login_response = requests.post(AUTH_URL, json={
        "email": "admin2@mifumo.com",
        "password": "admin123"
    })

    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get('tokens', {}).get('access')
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return

    headers = {'Authorization': f'Bearer {access_token}'}

    # Test with correct sender name length (max 11 characters)
    unique_name = f"TEST{int(time.time()) % 10000}"[:11]  # Ensure max 11 chars
    print(f"Testing with sender name: {unique_name} (length: {len(unique_name)})")

    form_data = {
        'sender_name': unique_name,
        'use_case': f'Test request with sender name {unique_name} for verification.'
    }

    submit_response = requests.post(SUBMIT_URL, data=form_data, headers=headers)
    print(f"Submit Status: {submit_response.status_code}")

    if submit_response.status_code == 201:
        data = submit_response.json()
        print("✅ Submit successful!")
        print(f"Request ID: {data.get('data', {}).get('id')}")
        print(f"Status: {data.get('data', {}).get('status')}")
        return data.get('data', {}).get('id')
    else:
        print(f"❌ Submit failed: {submit_response.text}")
        return None

if __name__ == "__main__":
    test_final_verification()
