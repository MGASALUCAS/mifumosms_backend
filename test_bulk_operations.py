#!/usr/bin/env python3
"""
Comprehensive tests for bulk operations and user profile settings endpoints.
"""

import json
import requests
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def register_user(self, email, password, first_name="Test", last_name="User"):
        """Register a new user."""
        url = f"{self.base_url}/accounts/register/"
        data = {
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": "+255700000001"
        }
        
        response = self.session.post(url, json=data)
        print(f"Register User: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            self.access_token = result['tokens']['access']
            self.user_id = result['user']['id']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"✓ User registered successfully: {email}")
            return True
        else:
            print(f"✗ Registration failed: {response.text}")
            return False
    
    def login_user(self, email, password):
        """Login user."""
        url = f"{self.base_url}/accounts/login/"
        data = {"email": email, "password": password}
        
        response = self.session.post(url, json=data)
        print(f"Login User: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['tokens']['access']
            self.user_id = result['user']['id']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"✓ User logged in successfully: {email}")
            return True
        else:
            print(f"✗ Login failed: {response.text}")
            return False
    
    def create_test_contacts(self, count=5):
        """Create test contacts for bulk operations."""
        contacts = []
        url = f"{self.base_url}/messaging/contacts/"
        
        for i in range(count):
            data = {
                "name": f"Test Contact {i+1}",
                "phone_e164": f"+25570000000{i+1}",
                "email": f"contact{i+1}@example.com",
                "tags": ["test", f"group{i+1}"]
            }
            
            response = self.session.post(url, json=data)
            if response.status_code == 201:
                contact = response.json()
                contacts.append(contact)
                print(f"✓ Created contact: {contact['name']}")
            else:
                print(f"✗ Failed to create contact {i+1}: {response.text}")
        
        return contacts
    
    def test_bulk_edit_contacts(self, contact_ids):
        """Test bulk edit contacts endpoint."""
        print("\n=== Testing Bulk Edit Contacts ===")
        url = f"{self.base_url}/messaging/contacts/bulk-edit/"
        
        data = {
            "contact_ids": contact_ids,
            "updates": {
                "tags": ["updated", "bulk_edited"],
                "is_active": True
            }
        }
        
        response = self.session.post(url, json=data)
        print(f"Bulk Edit Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Bulk edit successful: {result['message']}")
            print(f"  Updated: {result['updated_count']} contacts")
            return True
        else:
            print(f"✗ Bulk edit failed: {response.text}")
            return False
    
    def test_bulk_delete_contacts(self, contact_ids):
        """Test bulk delete contacts endpoint."""
        print("\n=== Testing Bulk Delete Contacts ===")
        url = f"{self.base_url}/messaging/contacts/bulk-delete/"
        
        data = {
            "contact_ids": contact_ids
        }
        
        response = self.session.post(url, json=data)
        print(f"Bulk Delete Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Bulk delete successful: {result['message']}")
            print(f"  Deleted: {result['deleted_count']} contacts")
            return True
        else:
            print(f"✗ Bulk delete failed: {response.text}")
            return False
    
    def test_phone_contact_import(self):
        """Test phone contact picker import."""
        print("\n=== Testing Phone Contact Import ===")
        url = f"{self.base_url}/messaging/contacts/import/"
        
        data = {
            "contacts": [
                {
                    "full_name": "John Doe",
                    "phone": "+255700000100",
                    "email": "john@example.com"
                },
                {
                    "full_name": "Jane Smith",
                    "phone": "+255700000101",
                    "email": "jane@example.com"
                },
                {
                    "full_name": "Bob Johnson",
                    "phone": "255700000102",  # Test without +
                    "email": "bob@example.com"
                }
            ]
        }
        
        response = self.session.post(url, json=data)
        print(f"Phone Import Response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Phone import successful: {result['message']}")
            print(f"  Imported: {result['imported']} contacts")
            print(f"  Skipped: {result['skipped']} contacts")
            return True
        else:
            print(f"✗ Phone import failed: {response.text}")
            return False

    def test_unified_bulk_import(self):
        """Test unified bulk import for both CSV and phone contacts."""
        print("\n=== Testing Unified Bulk Import ===")
        url = f"{self.base_url}/messaging/contacts/bulk-import/"
        
        # Test CSV import
        print("Testing CSV Import...")
        csv_data = {
            "import_type": "csv",
            "csv_data": "name,phone_e164,email,tags\nTest CSV Contact,+255700000200,csv@example.com,test,csv\nAnother CSV Contact,+255700000201,another@example.com,test",
            "skip_duplicates": True,
            "update_existing": False
        }
        
        response = self.session.post(url, json=csv_data)
        print(f"CSV Import Response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ CSV import successful: {result['message']}")
            print(f"  Imported: {result['imported']} contacts")
            print(f"  Updated: {result['updated']} contacts")
            print(f"  Skipped: {result['skipped']} contacts")
        else:
            print(f"✗ CSV import failed: {response.text}")
        
        # Test phone contacts import
        print("Testing Phone Contacts Import...")
        phone_data = {
            "import_type": "phone_contacts",
            "contacts": [
                {
                    "full_name": "Phone Contact 1",
                    "phone": "+255700000300",
                    "email": "phone1@example.com"
                },
                {
                    "full_name": "Phone Contact 2",
                    "phone": "+255700000301",
                    "email": "phone2@example.com"
                }
            ],
            "skip_duplicates": True,
            "update_existing": False
        }
        
        response = self.session.post(url, json=phone_data)
        print(f"Phone Contacts Import Response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Phone contacts import successful: {result['message']}")
            print(f"  Imported: {result['imported']} contacts")
            print(f"  Updated: {result['updated']} contacts")
            print(f"  Skipped: {result['skipped']} contacts")
            return True
        else:
            print(f"✗ Phone contacts import failed: {response.text}")
            return False
    
    def test_user_profile_settings(self):
        """Test user profile settings endpoints."""
        print("\n=== Testing User Profile Settings ===")
        
        # Test GET profile settings
        url = f"{self.base_url}/accounts/settings/profile/"
        response = self.session.get(url)
        print(f"Get Profile Settings: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Profile settings retrieved: {result['data']}")
        else:
            print(f"✗ Failed to get profile settings: {response.text}")
            return False
        
        # Test UPDATE profile settings
        update_data = {
            "first_name": "Updated First",
            "last_name": "Updated Last",
            "phone_number": "+255700000999"
        }
        
        response = self.session.put(url, json=update_data)
        print(f"Update Profile Settings: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Profile settings updated: {result['message']}")
            print(f"  New data: {result['data']}")
        else:
            print(f"✗ Failed to update profile settings: {response.text}")
            return False
        
        return True
    
    def test_user_preferences(self):
        """Test user preferences endpoints."""
        print("\n=== Testing User Preferences ===")
        
        url = f"{self.base_url}/accounts/settings/preferences/"
        
        # Test GET preferences
        response = self.session.get(url)
        print(f"Get Preferences: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Preferences retrieved: {result['data']}")
        else:
            print(f"✗ Failed to get preferences: {response.text}")
            return False
        
        # Test UPDATE preferences
        update_data = {
            "timezone": "Africa/Dar_es_Salaam"
        }
        
        response = self.session.put(url, json=update_data)
        print(f"Update Preferences: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Preferences updated: {result['message']}")
            print(f"  New data: {result['data']}")
        else:
            print(f"✗ Failed to update preferences: {response.text}")
            return False
        
        return True
    
    def test_user_notifications(self):
        """Test user notifications endpoints."""
        print("\n=== Testing User Notifications ===")
        
        url = f"{self.base_url}/accounts/settings/notifications/"
        
        # Test GET notifications
        response = self.session.get(url)
        print(f"Get Notifications: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Notifications retrieved: {result['data']}")
        else:
            print(f"✗ Failed to get notifications: {response.text}")
            return False
        
        # Test UPDATE notifications
        update_data = {
            "email_notifications": True,
            "sms_notifications": True
        }
        
        response = self.session.put(url, json=update_data)
        print(f"Update Notifications: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Notifications updated: {result['message']}")
            print(f"  New data: {result['data']}")
        else:
            print(f"✗ Failed to update notifications: {response.text}")
            return False
        
        return True
    
    def test_user_security(self):
        """Test user security endpoints."""
        print("\n=== Testing User Security ===")
        
        url = f"{self.base_url}/accounts/settings/security/"
        
        # Test GET security settings
        response = self.session.get(url)
        print(f"Get Security Settings: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Security settings retrieved: {result['data']}")
        else:
            print(f"✗ Failed to get security settings: {response.text}")
            return False
        
        return True
    
    def test_password_reset(self):
        """Test password reset functionality."""
        print("\n=== Testing Password Reset ===")
        
        # Test forgot password
        url = f"{self.base_url}/accounts/forgot-password/"
        data = {"email": TEST_EMAIL}
        
        response = self.session.post(url, json=data)
        print(f"Forgot Password: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Forgot password request successful: {result['message']}")
        else:
            print(f"✗ Forgot password failed: {response.text}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Comprehensive API Tests")
        print("=" * 50)
        
        # Register and login
        if not self.register_user(TEST_EMAIL, TEST_PASSWORD):
            print("❌ Cannot proceed without user registration")
            return
        
        # Test bulk operations
        contacts = self.create_test_contacts(3)
        if contacts:
            contact_ids = [contact['id'] for contact in contacts]
            
            # Test bulk edit
            self.test_bulk_edit_contacts(contact_ids[:2])  # Edit first 2
            
            # Test bulk delete
            self.test_bulk_delete_contacts(contact_ids[2:])  # Delete last 1
        
        # Test phone contact import
        self.test_phone_contact_import()
        
        # Test unified bulk import
        self.test_unified_bulk_import()
        
        # Test user profile settings
        self.test_user_profile_settings()
        self.test_user_preferences()
        self.test_user_notifications()
        self.test_user_security()
        
        # Test password reset
        self.test_password_reset()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")

def main():
    """Main test function."""
    tester = APITester(BASE_URL)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
