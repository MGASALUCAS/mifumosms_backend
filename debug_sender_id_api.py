#!/usr/bin/env python3
"""
Test script to debug sender ID API fetching issues.
This script tests all sender ID related endpoints to identify the problem.
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "test-sender-debug@example.com"
TEST_USER_PASSWORD = "testpass123"

class SenderIDDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def authenticate(self):
        """Authenticate and get access token."""
        print("🔐 Authenticating...")
        
        # Try to register first
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "SenderDebug"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/accounts/register/", json=register_data)
            if response.status_code in [200, 201, 400]:  # 400 might mean user exists
                print("✓ Registration attempt completed")
        except:
            print("⚠ Registration failed, trying login...")
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/accounts/login/", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            print("✓ Authentication successful")
            return True
        else:
            print(f"✗ Authentication failed: {response.text}")
            return False

    def test_sender_ids_list(self):
        """Test /api/messaging/sender-ids/ endpoint."""
        print("\n=== Testing Sender IDs List ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-ids/")
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sender IDs list retrieved successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('success') and result.get('data'):
                print(f"  Found {len(result['data'])} sender IDs")
                for sender_id in result['data']:
                    print(f"    - {sender_id['sender_id']} ({sender_id['status']})")
                return True
            else:
                print("❌ No sender IDs found in response")
                return False
        else:
            print(f"✗ Sender IDs list failed: {response.text}")
            return False

    def test_available_sender_ids(self):
        """Test /api/messaging/sender-requests/available/ endpoint."""
        print("\n=== Testing Available Sender IDs ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/available/")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Available sender IDs retrieved successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            available_ids = result.get('available_sender_ids', [])
            print(f"  Found {len(available_ids)} available sender IDs")
            for sender_id in available_ids:
                print(f"    - {sender_id.get('requested_sender_id', 'N/A')}")
            return True
        else:
            print(f"✗ Available sender IDs failed: {response.text}")
            return False

    def test_default_sender_overview(self):
        """Test /api/messaging/sender-requests/default/overview/ endpoint."""
        print("\n=== Testing Default Sender Overview ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/default/overview/")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Default sender overview retrieved successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            data = result.get('data', {})
            print(f"  Default sender: {data.get('default_sender')}")
            print(f"  Current sender ID: {data.get('current_sender_id')}")
            print(f"  Is available: {data.get('is_available')}")
            return True
        else:
            print(f"✗ Default sender overview failed: {response.text}")
            return False

    def test_sender_request_status(self):
        """Test /api/messaging/sender-requests/status/ endpoint."""
        print("\n=== Testing Sender Request Status ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/status/")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sender request status retrieved successfully")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            requests = result.get('sender_id_requests', [])
            print(f"  Found {len(requests)} sender ID requests")
            for req in requests:
                print(f"    - {req.get('requested_sender_id')} ({req.get('status')})")
            return True
        else:
            print(f"✗ Sender request status failed: {response.text}")
            return False

    def test_database_directly(self):
        """Test database directly to see what's stored."""
        print("\n=== Testing Database Directly ===")
        
        # This would require Django shell access
        print("To test database directly, run:")
        print("python manage.py shell")
        print("Then run:")
        print("from messaging.models_sms import SMSSenderID")
        print("from tenants.models import Tenant")
        print("from django.contrib.auth import get_user_model")
        print("User = get_user_model()")
        print("user = User.objects.get(email='test-sender-debug@example.com')")
        print("tenant = user.tenant")
        print("sender_ids = SMSSenderID.objects.filter(tenant=tenant)")
        print("for sid in sender_ids: print(f'{sid.sender_id} - {sid.status}')")

    def test_all_endpoints(self):
        """Test all sender ID related endpoints."""
        print("🧪 Testing All Sender ID Endpoints")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        tests = [
            self.test_sender_ids_list,
            self.test_available_sender_ids,
            self.test_default_sender_overview,
            self.test_sender_request_status,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                print()
        
        print("=" * 50)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All sender ID API tests passed!")
            return True
        else:
            print("❌ Some sender ID API tests failed.")
            return False

def main():
    """Main test function."""
    debugger = SenderIDDebugger()
    success = debugger.test_all_endpoints()
    
    if success:
        print("\n✅ All sender ID APIs are working correctly!")
        print("\n📋 API Endpoints to check in frontend:")
        print("  GET /api/messaging/sender-ids/")
        print("  GET /api/messaging/sender-requests/available/")
        print("  GET /api/messaging/sender-requests/default/overview/")
        print("  GET /api/messaging/sender-requests/status/")
    else:
        print("\n❌ Sender ID APIs need attention.")
        print("\n🔧 Debugging steps:")
        print("1. Check if user has a tenant")
        print("2. Check if tenant has sender IDs")
        print("3. Check if sender IDs are active")
        print("4. Check API endpoint URLs")
        print("5. Check authentication")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
