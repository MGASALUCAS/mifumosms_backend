#!/usr/bin/env python3
"""
Test script for the new CSV bulk import format.
Tests the exact format shown in the image: name, phone, local_number
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

BASE_URL = "http://127.0.0.1:8001/api"
TEST_USER_EMAIL = "notification-test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def get_jwt_token():
    """Get JWT token for authentication."""
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD
        })
        response.raise_for_status()
        return response.json()['tokens']['access']
    except requests.exceptions.RequestException as e:
        print(f"Error getting JWT token: {e}")
        return None

def test_csv_import_format():
    """Test the new CSV import format matching the image."""
    print("🧪 Testing New CSV Import Format")
    print("=" * 50)
    
    access_token = get_jwt_token()
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test CSV data matching the image format exactly
    csv_data = """name,phone,local_number
John Mkumbo,+255672883530,672883530
Fatma Mbwana,+255771978307,771978307
Juma Shaaban,+255712345678,712345678
Gloria Kimaro,+255765432109,765432109
Hassan Ndallahwa,+255789012345,789012345
Gloria Kassim,+255723456789,723456789
Asha Shayo,+255734567890,734567890
Grace Masika,+255745678901,745678901
Halima Lukindo,+255756789012,756789012
Juma Kapaya,+255767890123,767890123"""
    
    print("📄 CSV Data to Import:")
    print(csv_data)
    print()
    
    # Test the bulk import endpoint
    payload = {
        'import_type': 'csv',
        'csv_data': csv_data,
        'skip_duplicates': True,
        'update_existing': False
    }
    
    print("🚀 Sending CSV import request...")
    try:
        response = requests.post(
            f"{BASE_URL}/messaging/contacts/bulk-import/",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"📈 Imported: {data.get('imported', 0)}")
            print(f"📈 Updated: {data.get('updated', 0)}")
            print(f"📈 Skipped: {data.get('skipped', 0)}")
            print(f"📈 Total Processed: {data.get('total_processed', 0)}")
            print(f"📈 Errors: {len(data.get('errors', []))}")
            
            if data.get('errors'):
                print("\n❌ Errors:")
                for error in data['errors']:
                    print(f"   - {error}")
            
            print(f"\n💬 Message: {data.get('message', 'No message')}")
            
        else:
            print("❌ FAILED!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_phone_formats():
    """Test different phone number formats."""
    print("\n🧪 Testing Phone Number Formats")
    print("=" * 50)
    
    access_token = get_jwt_token()
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test different phone formats
    test_cases = [
        {
            'name': 'Format Test 1',
            'csv_data': 'name,phone,local_number\nTest User 1,+255712345678,712345678',
            'expected': 'Should work with +255 format'
        },
        {
            'name': 'Format Test 2', 
            'csv_data': 'name,phone,local_number\nTest User 2,255712345679,712345679',
            'expected': 'Should work with 255 format'
        },
        {
            'name': 'Format Test 3',
            'csv_data': 'name,phone,local_number\nTest User 3,0712345680,712345680',
            'expected': 'Should work with 0 format'
        },
        {
            'name': 'Format Test 4',
            'csv_data': 'name,phone,local_number\nTest User 4,712345681,712345681',
            'expected': 'Should work with local format'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 Test Case {i}: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        
        payload = {
            'import_type': 'csv',
            'csv_data': test_case['csv_data'],
            'skip_duplicates': True,
            'update_existing': False
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/messaging/contacts/bulk-import/",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ SUCCESS - Imported: {data.get('imported', 0)}")
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

def main():
    """Run all tests."""
    print("🚀 CSV Format Testing Suite")
    print("=" * 60)
    print("Testing the exact format from the image: name, phone, local_number")
    print()
    
    # Test the main CSV format
    test_csv_import_format()
    
    # Test different phone formats
    test_phone_formats()
    
    print("\n🎯 Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
