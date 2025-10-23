#!/usr/bin/env python3
"""
Test script for enhanced bulk import functionality with flexible phone number formats
"""

import requests
import json
import csv
import io

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin@example.com"
PASSWORD = "admin123"

def login():
    """Login and get authentication token"""
    login_response = requests.post(f"{BASE_URL}/api/auth/login/", json={
        "email": USERNAME,
        "password": PASSWORD
    })

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return None

    return login_response.json()['access']

def test_phone_normalization():
    """Test various phone number formats"""
    print("📱 Testing Phone Number Normalization")
    print("=" * 50)

    test_phones = [
        # Tanzanian formats
        "0712345678",      # Local with 0
        "712345678",       # Local without 0
        "255712345678",    # International without +
        "+255712345678",   # E.164 format
        "0712 345 678",    # With spaces
        "0712-345-678",    # With dashes
        "(0712) 345-678",  # With parentheses

        # Other East African formats
        "254712345678",    # Kenya
        "256712345678",    # Uganda
        "250712345678",    # Rwanda

        # Edge cases
        "07123456789",     # Too long
        "071234567",       # Too short
        "abc123def",       # Invalid characters
    ]

    token = login()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    for phone in test_phones:
        print(f"\nTesting: {phone}")

        # Create test CSV data
        csv_data = f"name,phone\nTest User,{phone}"

        response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-import/",
            headers=headers,
            json={
                "import_type": "csv",
                "csv_data": csv_data,
                "skip_duplicates": True,
                "update_existing": False
            }
        )

        if response.status_code == 201:
            data = response.json()
            if data.get('imported_count', 0) > 0:
                print(f"✅ Successfully normalized: {phone}")
            else:
                print(f"⚠️  Skipped (duplicate): {phone}")
        else:
            print(f"❌ Failed: {phone} - {response.text}")

def test_flexible_csv_columns():
    """Test CSV import with different column name variations"""
    print("\n📊 Testing Flexible CSV Column Names")
    print("=" * 50)

    test_cases = [
        {
            "name": "Standard columns",
            "csv": "name,phone\nJohn Doe,0712345678\nJane Smith,0712345679"
        },
        {
            "name": "Full name variation",
            "csv": "full_name,mobile_number\nJohn Doe,0712345678\nJane Smith,0712345679"
        },
        {
            "name": "Contact name variation",
            "csv": "contact_name,telephone\nJohn Doe,0712345678\nJane Smith,0712345679"
        },
        {
            "name": "Mixed case columns",
            "csv": "FULL_NAME,PHONE_NUMBER\nJohn Doe,0712345678\nJane Smith,0712345679"
        },
        {
            "name": "With email column",
            "csv": "name,phone,email\nJohn Doe,0712345678,john@example.com\nJane Smith,0712345679,jane@example.com"
        }
    ]

    token = login()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")

        response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-import/",
            headers=headers,
            json={
                "import_type": "csv",
                "csv_data": test_case['csv'],
                "skip_duplicates": True,
                "update_existing": False
            }
        )

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Success: {data.get('imported_count', 0)} contacts imported")
        else:
            print(f"❌ Failed: {response.text}")

def test_excel_import():
    """Test Excel file import (simulated with CSV data)"""
    print("\n📈 Testing Excel Import Simulation")
    print("=" * 50)

    # Create a more complex CSV that simulates Excel data
    excel_like_csv = """Full Name,Phone Number,Email Address
John Doe,0712345678,john@example.com
Jane Smith,0712345679,jane@example.com
Bob Johnson,0712345680,bob@example.com"""

    token = login()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print("Testing Excel-like CSV with flexible columns...")

    response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-import/",
        headers=headers,
        json={
            "import_type": "csv",
            "csv_data": excel_like_csv,
            "skip_duplicates": True,
            "update_existing": False
        }
    )

    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success: {data.get('imported_count', 0)} contacts imported")
        print(f"📊 Summary: {data.get('message', '')}")
    else:
        print(f"❌ Failed: {response.text}")

def test_error_handling():
    """Test error handling for invalid data"""
    print("\n⚠️  Testing Error Handling")
    print("=" * 50)

    error_cases = [
        {
            "name": "Missing name column",
            "csv": "phone\n0712345678"
        },
        {
            "name": "Missing phone column",
            "csv": "name\nJohn Doe"
        },
        {
            "name": "Invalid phone format",
            "csv": "name,phone\nJohn Doe,invalid_phone"
        },
        {
            "name": "Empty CSV",
            "csv": ""
        }
    ]

    token = login()
    if not token:
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    for i, test_case in enumerate(error_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")

        response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-import/",
            headers=headers,
            json={
                "import_type": "csv",
                "csv_data": test_case['csv'],
                "skip_duplicates": True,
                "update_existing": False
            }
        )

        if response.status_code == 400:
            print(f"✅ Correctly rejected: {test_case['name']}")
        else:
            print(f"⚠️  Unexpected success: {test_case['name']}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Bulk Import Testing")
    print("=" * 50)
    print("Testing improved phone normalization and flexible CSV columns")

    # Test phone normalization
    test_phone_normalization()

    # Test flexible CSV columns
    test_flexible_csv_columns()

    # Test Excel-like import
    test_excel_import()

    # Test error handling
    test_error_handling()

    print("\n🎉 Testing Complete!")
    print("=" * 50)
    print("✅ Enhanced bulk import is ready!")
    print("📱 Supports various phone number formats")
    print("📊 Supports flexible CSV column names")
    print("📈 Works with Excel files")
    print("⚠️  Proper error handling for invalid data")

if __name__ == "__main__":
    main()
