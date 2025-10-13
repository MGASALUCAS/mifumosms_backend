#!/usr/bin/env python
"""
Test script to verify the sender name request API is working.
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
SENDER_REQUEST_URL = f"{BASE_URL}/messaging/sender-requests/"

def test_api_without_auth():
    """Test API without authentication to see the error type."""
    print("🧪 Testing API without authentication...")

    try:
        response = requests.get(f"{SENDER_REQUEST_URL}stats/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 401:
            print("✅ API is working - returns 401 Unauthorized (expected)")
        elif response.status_code == 403:
            print("❌ API still returns 403 Forbidden (not fixed)")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_api_with_invalid_auth():
    """Test API with invalid authentication."""
    print("\n🧪 Testing API with invalid authentication...")

    headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{SENDER_REQUEST_URL}stats/", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 401:
            print("✅ API is working - returns 401 Unauthorized (expected)")
        elif response.status_code == 403:
            print("❌ API still returns 403 Forbidden (not fixed)")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_login():
    """Test login to get a valid token."""
    print("\n🧪 Testing login...")

    # Try common test credentials
    test_credentials = [
        {"email": "admin@example.com", "password": "admin123"},
        {"email": "test@example.com", "password": "test123"},
        {"email": "user@example.com", "password": "password123"},
    ]

    for creds in test_credentials:
        try:
            response = requests.post(AUTH_URL, json=creds)
            print(f"Login attempt with {creds['email']}: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                token = data.get('tokens', {}).get('access')
                if token:
                    print(f"✅ Login successful! Token: {token[:20]}...")
                    return token
                else:
                    print("❌ No token in response")
            else:
                print(f"❌ Login failed: {response.text}")

        except Exception as e:
            print(f"❌ Login error: {str(e)}")

    return None

def test_api_with_valid_auth(token):
    """Test API with valid authentication."""
    if not token:
        print("\n❌ No valid token available")
        return

    print(f"\n🧪 Testing API with valid authentication...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Test stats endpoint
        response = requests.get(f"{SENDER_REQUEST_URL}stats/", headers=headers)
        print(f"Stats endpoint - Status Code: {response.status_code}")
        print(f"Stats endpoint - Response: {response.text}")

        if response.status_code == 200:
            print("✅ Stats endpoint working!")
        elif response.status_code == 403:
            print("❌ Stats endpoint still returns 403 Forbidden")
        else:
            print(f"⚠️  Stats endpoint unexpected status: {response.status_code}")

        # Test list endpoint
        response = requests.get(f"{SENDER_REQUEST_URL}", headers=headers)
        print(f"\nList endpoint - Status Code: {response.status_code}")
        print(f"List endpoint - Response: {response.text}")

        if response.status_code == 200:
            print("✅ List endpoint working!")
        elif response.status_code == 403:
            print("❌ List endpoint still returns 403 Forbidden")
        else:
            print(f"⚠️  List endpoint unexpected status: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Sender Name Request API Fix")
    print("=" * 50)

    # Test without auth
    test_api_without_auth()

    # Test with invalid auth
    test_api_with_invalid_auth()

    # Try to get a valid token
    token = test_login()

    # Test with valid auth
    test_api_with_valid_auth(token)

    print("\n🎉 Testing completed!")
