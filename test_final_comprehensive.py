#!/usr/bin/env python3
"""
Final comprehensive test for sender ID functionality
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

def test_comprehensive():
    print("🎉 COMPREHENSIVE SENDER ID TEST")
    print("=" * 60)
    
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
    
    # Test endpoints
    base_url = "http://127.0.0.1:8001"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    endpoints = [
        ('/api/messaging/sender-ids/', 'Sender IDs List'),
        ('/api/messaging/sender-requests/available/', 'Available Sender IDs'),
        ('/api/messaging/sender-requests/default/overview/', 'Default Sender Overview'),
    ]
    
    results = {}
    
    for path, name in endpoints:
        url = base_url + path
        print(f'\n🔍 Testing: {name}')
        print(f'URL: {url}')
        
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'✅ SUCCESS!')
                
                if path == '/api/messaging/sender-ids/':
                    print(f'📊 Sender IDs count: {len(data.get("data", []))}')
                    if data.get("data"):
                        sender = data["data"][0]
                        print(f'📝 Sample sender: {sender.get("sender_id")} (Status: {sender.get("status")})')
                
                elif path == '/api/messaging/sender-requests/available/':
                    available = data.get("available_sender_ids", [])
                    print(f'📊 Available sender IDs: {len(available)}')
                    if available:
                        print(f'📝 Available: {available[0].get("requested_sender_id")}')
                
                elif path == '/api/messaging/sender-requests/default/overview/':
                    print(f'📊 Default sender: {data.get("data", {}).get("default_sender")}')
                    print(f'📊 Is available: {data.get("data", {}).get("is_available")}')
                
                results[name] = True
                
            else:
                print(f'❌ Error: {response.text[:200]}')
                results[name] = False
                
        except Exception as e:
            print(f'❌ Exception: {e}')
            results[name] = False
    
    # Summary
    print(f'\n📊 FINAL RESULTS:')
    print("=" * 40)
    success_count = sum(results.values())
    total_count = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f'{status} {name}')
    
    print(f'\n🎯 Overall: {success_count}/{total_count} endpoints working')
    
    if success_count == total_count:
        print('\n🎉 ALL TESTS PASSED! Ready for live server deployment!')
        return True
    else:
        print('\n⚠️  Some tests failed. Check the output above.')
        return False

if __name__ == "__main__":
    success = test_comprehensive()
    if success:
        print("\n🚀 SYSTEM IS READY FOR LIVE SERVER DEPLOYMENT!")
    else:
        print("\n🔧 System needs attention before deployment.")
