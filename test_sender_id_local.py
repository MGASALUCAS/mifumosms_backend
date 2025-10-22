#!/usr/bin/env python3
"""
Test sender ID endpoints using Django test client
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_sender_id_endpoints():
    print("🧪 Testing Sender ID Endpoints")
    print("=" * 50)
    
    # Get a user with tenant
    user = User.objects.filter(memberships__isnull=False).first()
    if not user:
        print("❌ No users with tenants found")
        return False
    
    print(f"Testing with user: {user.email}")
    tenant = user.memberships.first().tenant
    print(f"Tenant: {tenant.name}")
    
    # Use DRF APIClient
    client = APIClient()
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test endpoints (try both with and without trailing slashes)
    endpoints = [
        ('/api/messaging/sender-ids', 'Sender IDs List (no slash)'),
        ('/api/messaging/sender-ids/', 'Sender IDs List (with slash)'),
        ('/api/messaging/sender-requests/available', 'Available Sender IDs (no slash)'),
        ('/api/messaging/sender-requests/available/', 'Available Sender IDs (with slash)'),
        ('/api/messaging/sender-requests/default/overview', 'Default Sender Overview (no slash)'),
        ('/api/messaging/sender-requests/default/overview/', 'Default Sender Overview (with slash)'),
    ]
    
    success_count = 0
    
    for url, name in endpoints:
        print(f'\n🔍 Testing: {name}')
        print(f'URL: {url}')
        
        try:
            response = client.get(url)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'✅ Success: {data.get("success", False)}')
                
                if 'data' in data:
                    print(f'📊 Data count: {len(data["data"])}')
                    if data["data"]:
                        print(f'📝 First item: {data["data"][0]}')
                
                success_count += 1
            else:
                print(f'❌ Error: {response.content[:200]}')
                
        except Exception as e:
            print(f'❌ Exception: {e}')
    
    print(f'\n📊 Results: {success_count}/{len(endpoints)} endpoints working')
    return success_count == len(endpoints)

if __name__ == "__main__":
    success = test_sender_id_endpoints()
    if success:
        print("\n🎉 All tests passed! Ready for live server deployment.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
