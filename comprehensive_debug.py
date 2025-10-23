#!/usr/bin/env python3
"""
Comprehensive debug test for bulk import
"""

import requests
import json
import csv
from io import StringIO

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login/", json={
        "email": "admin@mifumo.com",
        "password": "admin123"
    })

    if response.status_code == 200:
        data = response.json()
        return data.get('tokens', {}).get('access')
    return None

def test_comprehensive():
    """Comprehensive test to identify the issue"""
    print("🔍 Comprehensive Debug Test")
    print("=" * 50)

    token = get_auth_token()
    if not token:
        print("❌ No auth token")
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Test 1: Very simple CSV
    print("\n1. Testing with simple CSV:")
    csv_data = {
        "import_type": "csv",
        "csv_data": "name,phone\nJohn,+255712345678",
        "skip_duplicates": False,
        "update_existing": False
    }

    response = requests.post(
        f"{BASE_URL}/api/messaging/contacts/bulk-import/",
        headers=headers,
        json=csv_data
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    # Test 2: Check if contacts were actually created
    print("\n2. Checking if contacts were created:")
    contacts_response = requests.get(
        f"{BASE_URL}/api/messaging/contacts/",
        headers=headers
    )

    if contacts_response.status_code == 200:
        contacts_data = contacts_response.json()
        print(f"Total contacts: {contacts_data.get('count', 0)}")
        if contacts_data.get('results'):
            print("Recent contacts:")
            for contact in contacts_data['results'][:3]:
                print(f"  - {contact.get('name')}: {contact.get('phone_e164')}")
    else:
        print(f"Failed to get contacts: {contacts_response.status_code}")

    # Test 3: Test phone contacts import
    print("\n3. Testing phone contacts import:")
    phone_data = {
        "import_type": "phone_contacts",
        "contacts": [
            {"full_name": "Test User", "phone": "+255712345678"}
        ],
        "skip_duplicates": False,
        "update_existing": False
    }

    response2 = requests.post(
        f"{BASE_URL}/api/messaging/contacts/bulk-import/",
        headers=headers,
        json=phone_data
    )

    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")

if __name__ == "__main__":
    test_comprehensive()
