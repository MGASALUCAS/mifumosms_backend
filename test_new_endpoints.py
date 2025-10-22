#!/usr/bin/env python3
"""
Simple test script to verify new endpoints are working.
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_endpoints():
    """Test the new endpoints."""
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    session = requests.Session()
    
    print("🧪 Testing New Endpoints")
    print("=" * 40)
    
    # 1. Test user registration
    print("\n1. Testing User Registration...")
    register_data = {
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password,
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+255700000001"
    }
    
    response = session.post(f"{BASE_URL}/accounts/register/", json=register_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        print("   ✅ Registration successful")
        data = response.json()
        access_token = data['tokens']['access']
        session.headers.update({'Authorization': f'Bearer {access_token}'})
    else:
        print("   ❌ Registration failed")
        print(f"   Response: {response.text}")
        return
    
    # 2. Test user profile settings
    print("\n2. Testing User Profile Settings...")
    
    # GET profile settings
    response = session.get(f"{BASE_URL}/accounts/settings/profile/")
    print(f"   GET Profile: {response.status_code}")
    
    # UPDATE profile settings
    update_data = {
        "first_name": "Updated First",
        "last_name": "Updated Last",
        "phone_number": "+255700000999"
    }
    response = session.put(f"{BASE_URL}/accounts/settings/profile/", json=update_data)
    print(f"   UPDATE Profile: {response.status_code}")
    
    # 3. Test user preferences
    print("\n3. Testing User Preferences...")
    
    # GET preferences
    response = session.get(f"{BASE_URL}/accounts/settings/preferences/")
    print(f"   GET Preferences: {response.status_code}")
    
    # UPDATE preferences
    update_data = {"timezone": "Africa/Dar_es_Salaam"}
    response = session.put(f"{BASE_URL}/accounts/settings/preferences/", json=update_data)
    print(f"   UPDATE Preferences: {response.status_code}")
    
    # 4. Test user notifications
    print("\n4. Testing User Notifications...")
    
    # GET notifications
    response = session.get(f"{BASE_URL}/accounts/settings/notifications/")
    print(f"   GET Notifications: {response.status_code}")
    
    # UPDATE notifications
    update_data = {
        "email_notifications": True,
        "sms_notifications": True
    }
    response = session.put(f"{BASE_URL}/accounts/settings/notifications/", json=update_data)
    print(f"   UPDATE Notifications: {response.status_code}")
    
    # 5. Test user security
    print("\n5. Testing User Security...")
    
    # GET security settings
    response = session.get(f"{BASE_URL}/accounts/settings/security/")
    print(f"   GET Security: {response.status_code}")
    
    # 6. Test bulk operations
    print("\n6. Testing Bulk Operations...")
    
    # Create test contacts
    contacts = []
    for i in range(3):
        contact_data = {
            "name": f"Test Contact {i+1}",
            "phone_e164": f"+25570000000{i+1}",
            "email": f"contact{i+1}@example.com"
        }
        response = session.post(f"{BASE_URL}/messaging/contacts/", json=contact_data)
        if response.status_code == 201:
            contacts.append(response.json())
            print(f"   ✅ Created contact {i+1}")
        else:
            print(f"   ❌ Failed to create contact {i+1}")
    
    if contacts:
        contact_ids = [contact['id'] for contact in contacts]
        
        # Test bulk edit
        bulk_edit_data = {
            "contact_ids": contact_ids[:2],
            "updates": {
                "tags": ["updated", "bulk_edited"],
                "is_active": True
            }
        }
        response = session.post(f"{BASE_URL}/messaging/contacts/bulk-edit/", json=bulk_edit_data)
        print(f"   Bulk Edit: {response.status_code}")
        
        # Test bulk delete
        bulk_delete_data = {
            "contact_ids": contact_ids[2:]
        }
        response = session.post(f"{BASE_URL}/messaging/contacts/bulk-delete/", json=bulk_delete_data)
        print(f"   Bulk Delete: {response.status_code}")
    
    # 7. Test phone contact import
    print("\n7. Testing Phone Contact Import...")
    
    import_data = {
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
            }
        ]
    }
    response = session.post(f"{BASE_URL}/messaging/contacts/import/", json=import_data)
    print(f"   Phone Import: {response.status_code}")
    
    # 7.5. Test unified bulk import
    print("\n7.5. Testing Unified Bulk Import...")
    
    # Test CSV import
    csv_data = {
        "import_type": "csv",
        "csv_data": "name,phone_e164,email,tags\nUnified CSV Contact,+255700000400,unified@example.com,test",
        "skip_duplicates": True,
        "update_existing": False
    }
    response = session.post(f"{BASE_URL}/messaging/contacts/bulk-import/", json=csv_data)
    print(f"   CSV Bulk Import: {response.status_code}")
    
    # Test phone contacts import
    phone_bulk_data = {
        "import_type": "phone_contacts",
        "contacts": [
            {
                "full_name": "Bulk Phone Contact",
                "phone": "+255700000401",
                "email": "bulk@example.com"
            }
        ],
        "skip_duplicates": True,
        "update_existing": False
    }
    response = session.post(f"{BASE_URL}/messaging/contacts/bulk-import/", json=phone_bulk_data)
    print(f"   Phone Bulk Import: {response.status_code}")
    
    # 8. Test password reset
    print("\n8. Testing Password Reset...")
    
    # Test forgot password
    reset_data = {"email": test_email}
    response = session.post(f"{BASE_URL}/accounts/forgot-password/", json=reset_data)
    print(f"   Forgot Password: {response.status_code}")
    
    print("\n" + "=" * 40)
    print("✅ All endpoint tests completed!")

if __name__ == "__main__":
    test_endpoints()
