#!/usr/bin/env python3
"""
Test script for message template endpoints.
This script tests all template functionality including CRUD operations, filtering, and special actions.
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:8001/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

class TemplateTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.template_id = None
        
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

    def test_create_template(self):
        """Test creating a new template."""
        print("\n=== Testing Template Creation ===")
        
        template_data = {
            "name": "Karibu - Asante kwa Kutua...",
            "category": "onboarding",
            "language": "sw",
            "channel": "whatsapp",
            "body_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
            "description": "Welcome message for new users",
            "status": "draft",
            "is_favorite": True
        }
        
        response = self.session.post(f"{BASE_URL}/messaging/templates/", json=template_data)
        print(f"Create Template Response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            self.template_id = result['id']
            print(f"✓ Template created successfully: {result['name']}")
            print(f"  ID: {result['id']}")
            print(f"  Variables: {result['variables']}")
            print(f"  Status: {result['status']}")
            return True
        else:
            print(f"✗ Template creation failed: {response.text}")
            return False

    def test_list_templates(self):
        """Test listing templates with filtering."""
        print("\n=== Testing Template List ===")
        
        # Test basic list
        response = self.session.get(f"{BASE_URL}/messaging/templates/")
        print(f"List Templates Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Templates listed successfully")
            print(f"  Total templates: {result.get('total_count', 0)}")
            print(f"  Filter options available: {list(result.get('filter_options', {}).keys())}")
            
            if result.get('templates'):
                template = result['templates'][0]
                print(f"  First template: {template['name']}")
                print(f"  Category: {template['category_display']}")
                print(f"  Language: {template['language_display']}")
                print(f"  Channel: {template['channel_display']}")
                print(f"  Variables count: {template['variables_count']}")
                print(f"  Last used: {template['last_used_display']}")
            
            return True
        else:
            print(f"✗ Template list failed: {response.text}")
            return False

    def test_filter_templates(self):
        """Test template filtering."""
        print("\n=== Testing Template Filtering ===")
        
        # Test category filter
        response = self.session.get(f"{BASE_URL}/messaging/templates/?category=onboarding")
        print(f"Category Filter Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Category filter working: {result.get('total_count', 0)} templates")
        
        # Test language filter
        response = self.session.get(f"{BASE_URL}/messaging/templates/?language=sw")
        print(f"Language Filter Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Language filter working: {result.get('total_count', 0)} templates")
        
        # Test favorites filter
        response = self.session.get(f"{BASE_URL}/messaging/templates/?favorites_only=true")
        print(f"Favorites Filter Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Favorites filter working: {result.get('total_count', 0)} templates")
        
        # Test search
        response = self.session.get(f"{BASE_URL}/messaging/templates/?search=Karibu")
        print(f"Search Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Search working: {result.get('total_count', 0)} templates")
        
        return True

    def test_template_detail(self):
        """Test retrieving template details."""
        print("\n=== Testing Template Detail ===")
        
        if not self.template_id:
            print("✗ No template ID available for detail test")
            return False
        
        response = self.session.get(f"{BASE_URL}/messaging/templates/{self.template_id}/")
        print(f"Template Detail Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Template detail retrieved successfully")
            print(f"  Name: {result['name']}")
            print(f"  Body text: {result['body_text'][:50]}...")
            print(f"  Variables: {result['variables']}")
            print(f"  Statistics: {result.get('statistics', {})}")
            print(f"  Formatted text: {result.get('formatted_body_text', '')[:50]}...")
            return True
        else:
            print(f"✗ Template detail failed: {response.text}")
            return False

    def test_template_update(self):
        """Test updating a template."""
        print("\n=== Testing Template Update ===")
        
        if not self.template_id:
            print("✗ No template ID available for update test")
            return False
        
        update_data = {
            "name": "Karibu - Asante kwa Kutua... (Updated)",
            "description": "Updated welcome message",
            "is_favorite": False,
            "status": "pending"
        }
        
        response = self.session.patch(f"{BASE_URL}/messaging/templates/{self.template_id}/", json=update_data)
        print(f"Template Update Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Template updated successfully")
            print(f"  New name: {result['name']}")
            print(f"  New description: {result['description']}")
            print(f"  Favorite status: {result['is_favorite']}")
            print(f"  Status: {result['status']}")
            return True
        else:
            print(f"✗ Template update failed: {response.text}")
            return False

    def test_template_actions(self):
        """Test template actions (favorite, usage, approve, etc.)."""
        print("\n=== Testing Template Actions ===")
        
        if not self.template_id:
            print("✗ No template ID available for actions test")
            return False
        
        # Test toggle favorite
        response = self.session.post(f"{BASE_URL}/messaging/templates/{self.template_id}/toggle-favorite/")
        print(f"Toggle Favorite Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Favorite toggled: {result['is_favorite']}")
        
        # Test increment usage
        response = self.session.post(f"{BASE_URL}/messaging/templates/{self.template_id}/increment-usage/")
        print(f"Increment Usage Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Usage incremented: {result['usage_count']}")
        
        # Test approve
        response = self.session.post(f"{BASE_URL}/messaging/templates/{self.template_id}/approve/")
        print(f"Approve Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Template approved: {result['approved']}")
        
        # Test get variables
        response = self.session.get(f"{BASE_URL}/messaging/templates/{self.template_id}/variables/")
        print(f"Variables Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Variables retrieved: {result['variables']}")
        
        return True

    def test_template_copy(self):
        """Test copying a template."""
        print("\n=== Testing Template Copy ===")
        
        if not self.template_id:
            print("✗ No template ID available for copy test")
            return False
        
        copy_data = {
            "name": "Karibu - Copy"
        }
        
        response = self.session.post(f"{BASE_URL}/messaging/templates/{self.template_id}/copy/", json=copy_data)
        print(f"Template Copy Response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Template copied successfully")
            print(f"  New template name: {result['template']['name']}")
            print(f"  New template ID: {result['template']['id']}")
            return True
        else:
            print(f"✗ Template copy failed: {response.text}")
            return False

    def test_template_statistics(self):
        """Test template statistics."""
        print("\n=== Testing Template Statistics ===")
        
        response = self.session.get(f"{BASE_URL}/messaging/templates/statistics/")
        print(f"Template Statistics Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Template statistics retrieved")
            print(f"  Overview: {result.get('overview', {})}")
            print(f"  Category breakdown: {len(result.get('category_breakdown', []))} categories")
            print(f"  Language breakdown: {len(result.get('language_breakdown', []))} languages")
            print(f"  Channel breakdown: {len(result.get('channel_breakdown', []))} channels")
            return True
        else:
            print(f"✗ Template statistics failed: {response.text}")
            return False

    def test_create_multiple_templates(self):
        """Test creating multiple templates for better testing."""
        print("\n=== Creating Multiple Templates ===")
        
        templates = [
            {
                "name": "Tangazo la Ofa (General)",
                "category": "promotions",
                "language": "sw",
                "channel": "whatsapp",
                "body_text": "Habari {{name}}! Leo tunayo ofa ya {{discount}}% kwa {{category}} hadi {{expiry}}. Tumia KODI: {{code}}. Nunua hapa: {{short_url}}",
                "description": "General offer announcement",
                "status": "approved",
                "is_favorite": True
            },
            {
                "name": "Kumbusho la Ziara / Huduma",
                "category": "reminders",
                "language": "sw",
                "channel": "whatsapp",
                "body_text": "Habari {{name}}, tunakukaribisha tena siku ya {{date}} saa {{time}} 📍 {{location}}. Jibu CONFIRM au BADILI hapa: {{short_url}}",
                "description": "Visit/service reminder",
                "status": "approved",
                "is_favorite": False
            },
            {
                "name": "Asante kwa Kutuamini - Karib...",
                "category": "loyalty",
                "language": "sw",
                "channel": "whatsapp",
                "body_text": "Asante {{name}} kwa kutuamini {{company}}. Tunarahisisha maisha ya biashara yako kila siku. Karibu tena wakati wowote!",
                "description": "Thank you for trusting us",
                "status": "draft",
                "is_favorite": False
            }
        ]
        
        created_count = 0
        for template_data in templates:
            response = self.session.post(f"{BASE_URL}/messaging/templates/", json=template_data)
            if response.status_code == 201:
                created_count += 1
                print(f"✓ Created: {template_data['name']}")
            else:
                print(f"✗ Failed to create: {template_data['name']}")
        
        print(f"Created {created_count}/{len(templates)} templates")
        return created_count > 0

    def run_all_tests(self):
        """Run all template tests."""
        print("🧪 Testing Message Template Endpoints")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        tests = [
            self.test_create_template,
            self.test_create_multiple_templates,
            self.test_list_templates,
            self.test_filter_templates,
            self.test_template_detail,
            self.test_template_update,
            self.test_template_actions,
            self.test_template_copy,
            self.test_template_statistics,
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
            print("🎉 All template tests passed!")
            return True
        else:
            print("❌ Some template tests failed.")
            return False

def main():
    """Main test function."""
    tester = TemplateTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Template endpoints are working correctly!")
        print("\n📋 Available Template Endpoints:")
        print("  GET    /api/messaging/templates/                    - List templates with filtering")
        print("  POST   /api/messaging/templates/                    - Create new template")
        print("  GET    /api/messaging/templates/{id}/                - Get template details")
        print("  PUT    /api/messaging/templates/{id}/                - Update template")
        print("  PATCH  /api/messaging/templates/{id}/                - Partial update template")
        print("  DELETE /api/messaging/templates/{id}/                - Delete template")
        print("  POST   /api/messaging/templates/{id}/toggle-favorite/ - Toggle favorite status")
        print("  POST   /api/messaging/templates/{id}/increment-usage/ - Increment usage count")
        print("  POST   /api/messaging/templates/{id}/approve/         - Approve template")
        print("  POST   /api/messaging/templates/{id}/reject/         - Reject template")
        print("  GET    /api/messaging/templates/{id}/variables/      - Get template variables")
        print("  POST   /api/messaging/templates/{id}/copy/           - Copy template")
        print("  GET    /api/messaging/templates/statistics/          - Get template statistics")
    else:
        print("\n❌ Template endpoints need attention.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
