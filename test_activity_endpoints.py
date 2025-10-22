#!/usr/bin/env python3
"""
Test script for activity and performance endpoints.
This script tests the recent activity and performance overview functionality.
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

class ActivityTester:
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
            "last_name": "User"
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

    def test_recent_activity(self):
        """Test recent activity endpoint."""
        print("\n=== Testing Recent Activity ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/activity/recent/")
        print(f"Recent Activity Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Recent activity retrieved successfully")
            print(f"  Total activities: {result['data']['total_count']}")
            print(f"  Live activities: {result['data']['live_count']}")
            print(f"  Has more: {result['data']['has_more']}")
            
            if result['data']['activities']:
                print("  Sample activities:")
                for i, activity in enumerate(result['data']['activities'][:3]):
                    print(f"    {i+1}. {activity['title']} ({activity['time_ago']})")
                    print(f"       Type: {activity['type']}")
                    print(f"       Live: {activity.get('is_live', False)}")
            
            return True
        else:
            print(f"✗ Recent activity failed: {response.text}")
            return False

    def test_recent_activity_with_filters(self):
        """Test recent activity with filters."""
        print("\n=== Testing Recent Activity with Filters ===")
        
        # Test with type filter
        response = self.session.get(f"{BASE_URL}/messaging/activity/recent/?type=conversation_reply")
        print(f"Filtered Activity Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Filtered activity retrieved successfully")
            print(f"  Activities count: {len(result['data']['activities'])}")
            
            # Check if all activities are of the filtered type
            for activity in result['data']['activities']:
                if activity['type'] != 'conversation_reply':
                    print(f"✗ Wrong activity type: {activity['type']}")
                    return False
            
            print("✓ All activities match the filter")
            return True
        else:
            print(f"✗ Filtered activity failed: {response.text}")
            return False

    def test_performance_overview(self):
        """Test performance overview endpoint."""
        print("\n=== Testing Performance Overview ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/performance/overview/")
        print(f"Performance Overview Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Performance overview retrieved successfully")
            
            metrics = result['data']['metrics']
            print(f"  Total messages: {metrics['total_messages']}")
            print(f"  Delivery rate: {metrics['delivery_rate']}%")
            print(f"  Response rate: {metrics['response_rate']}%")
            print(f"  Active conversations: {metrics['active_conversations']}")
            print(f"  Campaign success rate: {metrics['campaign_success_rate']}%")
            
            charts = result['data']['charts']
            print(f"  Charts available: {list(charts.keys())}")
            print(f"  Coming soon: {result['data']['coming_soon']}")
            
            return True
        else:
            print(f"✗ Performance overview failed: {response.text}")
            return False

    def test_activity_statistics(self):
        """Test activity statistics endpoint."""
        print("\n=== Testing Activity Statistics ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/activity/statistics/")
        print(f"Activity Statistics Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Activity statistics retrieved successfully")
            
            today = result['data']['today']
            week = result['data']['this_week']
            month = result['data']['this_month']
            
            print(f"  Today:")
            print(f"    Messages sent: {today['messages_sent']}")
            print(f"    Messages received: {today['messages_received']}")
            print(f"    Conversations started: {today['conversations_started']}")
            print(f"    Campaigns launched: {today['campaigns_launched']}")
            
            print(f"  This week:")
            print(f"    Messages sent: {week['messages_sent']}")
            print(f"    Messages received: {week['messages_received']}")
            print(f"    Conversations started: {week['conversations_started']}")
            print(f"    Campaigns launched: {week['campaigns_launched']}")
            
            print(f"  This month:")
            print(f"    Messages sent: {month['messages_sent']}")
            print(f"    Messages received: {month['messages_received']}")
            print(f"    Conversations started: {month['conversations_started']}")
            print(f"    Campaigns launched: {month['campaigns_launched']}")
            
            return True
        else:
            print(f"✗ Activity statistics failed: {response.text}")
            return False

    def test_create_sample_data(self):
        """Create some sample data for testing."""
        print("\n=== Creating Sample Data ===")
        
        # Create a sample template
        template_data = {
            "name": "Welcome Message - Swahili",
            "category": "onboarding",
            "language": "sw",
            "channel": "whatsapp",
            "body_text": "Habari {{name}}! Karibu kwenye {{company}}.",
            "description": "Welcome message for new users",
            "status": "approved",
            "is_favorite": True
        }
        
        response = self.session.post(f"{BASE_URL}/messaging/templates/", json=template_data)
        if response.status_code == 201:
            print("✓ Sample template created")
        
        # Create a sample contact
        contact_data = {
            "name": "John Kamau",
            "phone_e164": "+255700000001",
            "email": "john@example.com"
        }
        
        response = self.session.post(f"{BASE_URL}/messaging/contacts/", json=contact_data)
        if response.status_code == 201:
            print("✓ Sample contact created")
        
        return True

    def run_all_tests(self):
        """Run all activity tests."""
        print("🧪 Testing Activity & Performance Endpoints")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Create sample data first
        self.test_create_sample_data()
        
        tests = [
            self.test_recent_activity,
            self.test_recent_activity_with_filters,
            self.test_performance_overview,
            self.test_activity_statistics,
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
            print("🎉 All activity tests passed!")
            return True
        else:
            print("❌ Some activity tests failed.")
            return False

def main():
    """Main test function."""
    tester = ActivityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Activity endpoints are working correctly!")
        print("\n📋 Available Activity Endpoints:")
        print("  GET /api/messaging/activity/recent/                    - Recent activity feed")
        print("  GET /api/messaging/performance/overview/               - Performance overview")
        print("  GET /api/messaging/activity/statistics/                - Activity statistics")
        print("\n🔧 Query Parameters for Recent Activity:")
        print("  ?limit=10                                              - Limit number of activities")
        print("  ?type=conversation_reply                               - Filter by activity type")
        print("  ?type=campaign_completed                               - Filter by activity type")
        print("  ?type=contact_added                                    - Filter by activity type")
        print("  ?type=template_approved                                - Filter by activity type")
    else:
        print("\n❌ Activity endpoints need attention.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
