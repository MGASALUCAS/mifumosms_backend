#!/usr/bin/env python3
"""
Test sender ID API with actual HTTP requests
"""

import os
import sys
import django
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_sender_id_api():
    print("🧪 Testing Sender ID API with HTTP Requests")
    print("=" * 50)
    
    # Get a user with tenant
    user = User.objects.filter(memberships__isnull=False).first()
    if not user:
        print("❌ No users with tenants found")
        return False
    
    print(f"Testing with user: {user.email}")
    tenant = user.memberships.first().tenant
    print(f"Tenant: {tenant.name}")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Test endpoints
    base_url = "http://127.0.0.1:8001"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    endpoints = [
        ('/api/messaging/sender-ids/', 'Sender IDs List'),
        ('/api/messaging/sender-requests/available/', 'Available Sender IDs'),
        ('/api/messaging/sender-requests/default/overview/', 'Default Sender Overview'),
    ]
    
    success_count = 0
    
    for path, name in endpoints:
        url = base_url + path
        print(f'\n🔍 Testing: {name}')
        print(f'URL: {url}')
        
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'✅ Success: {data.get("success", False)}')
                
                if 'data' in data:
                    print(f'📊 Data count: {len(data["data"])}')
                    if data["data"]:
                        print(f'📝 First item keys: {list(data["data"][0].keys())}')
                        # Show specific data for sender IDs
                        if 'sender_id' in data["data"][0]:
                            print(f'📝 Sample sender ID: {data["data"][0]["sender_id"]}')
                        if 'is_available' in data["data"][0]:
                            print(f'📝 Is available: {data["data"][0]["is_available"]}')
                
                success_count += 1
            else:
                print(f'❌ Error: {response.text[:200]}')
                
        except Exception as e:
            print(f'❌ Exception: {e}')
    
    print(f'\n📊 Results: {success_count}/{len(endpoints)} endpoints working')
    return success_count == len(endpoints)

if __name__ == "__main__":
    success = test_sender_id_api()
    if success:
        print("\n🎉 All API tests passed! Ready for live server deployment.")
    else:
        print("\n⚠️  Some API tests failed. Check the output above.")
