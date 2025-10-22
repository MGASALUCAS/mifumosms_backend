#!/usr/bin/env python3
"""
Debug Bulk Import and Activity Statistics Issues
"""

import os
import sys
import django
import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_bulk_import():
    print("🔍 Testing Bulk Import Endpoint")
    print("=" * 50)
    
    # Get a user with tenant
    user = User.objects.filter(memberships__isnull=False).first()
    if not user:
        print("❌ No users with tenants found")
        return False
    
    print(f"👤 Testing with user: {user.email}")
    tenant = user.memberships.first().tenant
    print(f"🏢 Tenant: {tenant.name}")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Test both local and live server
    servers = [
        ("Local", "http://127.0.0.1:8001"),
        ("Live", "https://mifumosms.servehttp.com")
    ]
    
    for server_name, base_url in servers:
        print(f"\n🌐 Testing {server_name} Server: {base_url}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Phone contacts import
        print(f"\n📱 Testing Phone Contacts Import:")
        phone_contacts_data = {
            "import_type": "phone_contacts",
            "contacts": [
                {
                    "full_name": "John Doe",
                    "phone": "+255123456789",
                    "email": "john@example.com"
                },
                {
                    "full_name": "Jane Smith", 
                    "phone": "+255987654321",
                    "email": "jane@example.com"
                }
            ],
            "skip_duplicates": True,
            "update_existing": False
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/messaging/contacts/bulk-import/",
                headers=headers,
                json=phone_contacts_data,
                timeout=10,
                verify=False
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Success: {data.get('message', 'No message')}")
                print(f"📊 Imported: {data.get('imported', 0)}")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        # Test 2: CSV import
        print(f"\n📄 Testing CSV Import:")
        csv_data = {
            "import_type": "csv",
            "csv_data": "name,phone_e164,email\nJohn Doe,+255123456789,john@example.com\nJane Smith,+255987654321,jane@example.com",
            "skip_duplicates": True,
            "update_existing": False
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/messaging/contacts/bulk-import/",
                headers=headers,
                json=csv_data,
                timeout=10,
                verify=False
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Success: {data.get('message', 'No message')}")
                print(f"📊 Imported: {data.get('imported', 0)}")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_activity_statistics():
    print("\n🔍 Testing Activity Statistics Endpoint")
    print("=" * 50)
    
    # Get a user with tenant
    user = User.objects.filter(memberships__isnull=False).first()
    if not user:
        print("❌ No users with tenants found")
        return False
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Test both local and live server
    servers = [
        ("Local", "http://127.0.0.1:8001"),
        ("Live", "https://mifumosms.servehttp.com")
    ]
    
    for server_name, base_url in servers:
        print(f"\n🌐 Testing {server_name} Server: {base_url}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test activity endpoints
        endpoints = [
            "/api/messaging/activity/recent/",
            "/api/messaging/activity/statistics/",
            "/api/messaging/performance/overview/"
        ]
        
        for endpoint in endpoints:
            print(f"\n📊 Testing: {endpoint}")
            try:
                response = requests.get(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    timeout=10,
                    verify=False
                )
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Success: JSON response received")
                        if 'data' in data:
                            print(f"📊 Data keys: {list(data['data'].keys())}")
                    except json.JSONDecodeError:
                        print(f"❌ Error: Response is not valid JSON")
                        print(f"Response: {response.text[:200]}")
                else:
                    print(f"❌ Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 DEBUGGING BULK IMPORT AND ACTIVITY STATISTICS")
    print("=" * 60)
    
    test_bulk_import()
    test_activity_statistics()
    
    print("\n🎯 Debugging Complete!")
