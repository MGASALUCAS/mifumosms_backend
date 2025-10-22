#!/usr/bin/env python3
"""
Test script to verify default sender ID functionality.
This script tests that users now have default sender IDs available immediately.
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:8001/api"
TEST_USER_EMAIL = "test-default-sender@example.com"
TEST_USER_PASSWORD = "testpass123"

class DefaultSenderTester:
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
            "last_name": "DefaultSender"
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

    def test_default_sender_overview(self):
        """Test default sender ID overview endpoint."""
        print("\n=== Testing Default Sender ID Overview ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/default/overview/")
        print(f"Default Sender Overview Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Default sender overview retrieved successfully")
            
            data = result['data']
            print(f"  Default sender: {data['default_sender']}")
            print(f"  Current sender ID: {data['current_sender_id']}")
            print(f"  Is available: {data['is_available']}")
            print(f"  Can request: {data['can_request']}")
            print(f"  Reason: {data['reason']}")
            print(f"  Credits: {data['balance']['credits']}")
            print(f"  Needs purchase: {data['balance']['needs_purchase']}")
            
            # Check if default sender is available
            if data['is_available'] and data['current_sender_id'] == 'Taarifa-SMS':
                print("✅ Default sender ID is available and ready to use!")
                return True
            else:
                print("❌ Default sender ID is not available")
                return False
        else:
            print(f"✗ Default sender overview failed: {response.text}")
            return False

    def test_available_sender_ids(self):
        """Test available sender IDs endpoint."""
        print("\n=== Testing Available Sender IDs ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/available/")
        print(f"Available Sender IDs Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Available sender IDs retrieved successfully")
            
            available_ids = result['available_sender_ids']
            print(f"  Available sender IDs: {len(available_ids)}")
            
            for sender_id in available_ids:
                print(f"    - {sender_id['requested_sender_id']}")
            
            # Check if Taarifa-SMS is available
            taarifa_available = any(
                sid['requested_sender_id'] == 'Taarifa-SMS' 
                for sid in available_ids
            )
            
            if taarifa_available:
                print("✅ Taarifa-SMS is available in the list!")
                return True
            else:
                print("❌ Taarifa-SMS is not available")
                return False
        else:
            print(f"✗ Available sender IDs failed: {response.text}")
            return False

    def test_sender_ids_list(self):
        """Test sender IDs list endpoint."""
        print("\n=== Testing Sender IDs List ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-ids/")
        print(f"Sender IDs List Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sender IDs list retrieved successfully")
            
            sender_ids = result['data']
            print(f"  Active sender IDs: {len(sender_ids)}")
            
            for sender_id in sender_ids:
                print(f"    - {sender_id['sender_id']} ({sender_id['status']})")
            
            # Check if Taarifa-SMS is active
            taarifa_active = any(
                sid['sender_id'] == 'Taarifa-SMS' and sid['status'] == 'active'
                for sid in sender_ids
            )
            
            if taarifa_active:
                print("✅ Taarifa-SMS is active!")
                return True
            else:
                print("❌ Taarifa-SMS is not active")
                return False
        else:
            print(f"✗ Sender IDs list failed: {response.text}")
            return False

    def test_sender_request_status(self):
        """Test sender request status endpoint."""
        print("\n=== Testing Sender Request Status ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/sender-requests/status/")
        print(f"Sender Request Status Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sender request status retrieved successfully")
            
            sms_balance = result['sms_balance']
            print(f"  Credits: {sms_balance['credits']}")
            print(f"  Can request sender ID: {sms_balance['can_request_sender_id']}")
            
            requests = result['sender_id_requests']
            print(f"  Total requests: {len(requests)}")
            
            # Check for approved Taarifa-SMS request
            taarifa_approved = any(
                req['requested_sender_id'] == 'Taarifa-SMS' and req['status'] == 'approved'
                for req in requests
            )
            
            if taarifa_approved:
                print("✅ Taarifa-SMS request is approved!")
                return True
            else:
                print("❌ Taarifa-SMS request is not approved")
                return False
        else:
            print(f"✗ Sender request status failed: {response.text}")
            return False

    def run_all_tests(self):
        """Run all default sender ID tests."""
        print("🧪 Testing Default Sender ID Functionality")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        tests = [
            self.test_default_sender_overview,
            self.test_available_sender_ids,
            self.test_sender_ids_list,
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
            print("🎉 All default sender ID tests passed!")
            return True
        else:
            print("❌ Some default sender ID tests failed.")
            return False

def main():
    """Main test function."""
    tester = DefaultSenderTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Default sender ID functionality is working correctly!")
        print("\n📋 Key Points:")
        print("  ✓ New users automatically get 'Taarifa-SMS' as default sender ID")
        print("  ✓ Default sender ID is immediately available (no approval needed)")
        print("  ✓ Users can start sending SMS immediately (after purchasing credits)")
        print("  ✓ Frontend can show 'Available' status for default sender ID")
        print("\n🔧 Frontend Integration:")
        print("  GET /api/messaging/sender-requests/default/overview/")
        print("  GET /api/messaging/sender-requests/available/")
        print("  GET /api/messaging/sender-ids/")
        print("  GET /api/messaging/sender-requests/status/")
    else:
        print("\n❌ Default sender ID functionality needs attention.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
