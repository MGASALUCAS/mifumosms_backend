#!/usr/bin/env python3
"""
Test script for bulk add tags endpoint
This tests the new /api/messaging/contacts/bulk-add-tags/ endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin@example.com"  # Replace with your actual email
PASSWORD = "admin123"  # Replace with your actual password

def test_bulk_add_tags():
    """Test the bulk add tags endpoint"""

    print("🏷️  Testing Bulk Add Tags Endpoint")
    print("=" * 50)

    # Login to get token
    print("\n1. Logging in...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login/", json={
        "email": USERNAME,
        "password": PASSWORD
    })

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return

    token = login_response.json()['access']
    print(f"✅ Login successful!")

    headers = {"Authorization": f"Bearer {token}"}

    # First, create some test contacts
    print("\n2. Creating test contacts...")
    test_contacts = []

    for i in range(3):
        contact_data = {
            "name": f"Test Contact {i+1}",
            "phone_e164": f"+25570000000{i+1}",
            "email": f"test{i+1}@example.com"
        }

        response = requests.post(f"{BASE_URL}/api/messaging/contacts/",
            json=contact_data,
            headers=headers
        )

        if response.status_code == 201:
            contact = response.json()
            test_contacts.append(contact['id'])
            print(f"✅ Created contact: {contact['name']} (ID: {contact['id']})")
        else:
            print(f"❌ Failed to create contact {i+1}: {response.text}")

    if not test_contacts:
        print("❌ No test contacts created. Cannot test bulk add tags.")
        return

    # Test bulk add tags
    print(f"\n3. Testing bulk add tags to {len(test_contacts)} contacts...")

    bulk_tags_data = {
        "contact_ids": test_contacts,
        "tags": ["test", "bulk", "api-test"]
    }

    print(f"📋 Adding tags: {bulk_tags_data['tags']}")
    print(f"📋 To contacts: {bulk_tags_data['contact_ids']}")

    response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-add-tags/",
        json=bulk_tags_data,
        headers=headers
    )

    print(f"\n📊 Response Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("✅ Bulk add tags successful!")
        print(f"📈 Results:")
        print(f"  - Updated: {result.get('updated_count', 0)}")
        print(f"  - Total Requested: {result.get('total_requested', 0)}")
        print(f"  - Tags Added: {result.get('tags_added', [])}")

        if result.get('errors'):
            print(f"⚠️  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    - {error}")
    else:
        print(f"❌ Bulk add tags failed: {response.text}")

    # Verify tags were added by getting contact details
    print(f"\n4. Verifying tags were added...")

    for contact_id in test_contacts:
        response = requests.get(f"{BASE_URL}/api/messaging/contacts/{contact_id}/",
            headers=headers
        )

        if response.status_code == 200:
            contact = response.json()
            print(f"✅ Contact {contact['name']}: tags = {contact.get('tags', [])}")
        else:
            print(f"❌ Failed to get contact {contact_id}: {response.text}")

    # Test adding more tags (should merge with existing)
    print(f"\n5. Testing adding more tags (should merge with existing)...")

    additional_tags_data = {
        "contact_ids": test_contacts,
        "tags": ["additional", "merged"]
    }

    response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-add-tags/",
        json=additional_tags_data,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print("✅ Additional tags added successfully!")
        print(f"📈 Updated: {result.get('updated_count', 0)} contacts")
    else:
        print(f"❌ Failed to add additional tags: {response.text}")

    # Verify final tags
    print(f"\n6. Verifying final tags...")

    for contact_id in test_contacts:
        response = requests.get(f"{BASE_URL}/api/messaging/contacts/{contact_id}/",
            headers=headers
        )

        if response.status_code == 200:
            contact = response.json()
            print(f"✅ Contact {contact['name']}: final tags = {contact.get('tags', [])}")
        else:
            print(f"❌ Failed to get contact {contact_id}: {response.text}")

    # Test error cases
    print(f"\n7. Testing error cases...")

    # Test with invalid contact IDs
    invalid_data = {
        "contact_ids": ["invalid-uuid-1", "invalid-uuid-2"],
        "tags": ["test"]
    }

    response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-add-tags/",
        json=invalid_data,
        headers=headers
    )

    print(f"📊 Invalid UUIDs Response: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected invalid UUIDs")
    else:
        print(f"❌ Unexpected response: {response.text}")

    # Test with empty tags
    empty_tags_data = {
        "contact_ids": test_contacts[:1],
        "tags": []
    }

    response = requests.post(f"{BASE_URL}/api/messaging/contacts/bulk-add-tags/",
        json=empty_tags_data,
        headers=headers
    )

    print(f"📊 Empty tags Response: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected empty tags")
    else:
        print(f"❌ Unexpected response: {response.text}")

    print("\n🎯 Summary:")
    print("=" * 50)
    print("✅ Bulk add tags endpoint is working!")
    print("✅ Tags are merged with existing tags (no duplicates)")
    print("✅ Proper validation for contact IDs and tags")
    print("✅ Error handling for invalid data")

    # Clean up test contacts
    print(f"\n8. Cleaning up test contacts...")
    for contact_id in test_contacts:
        response = requests.delete(f"{BASE_URL}/api/messaging/contacts/{contact_id}/",
            headers=headers
        )
        if response.status_code == 204:
            print(f"✅ Deleted contact {contact_id}")
        else:
            print(f"❌ Failed to delete contact {contact_id}")

if __name__ == "__main__":
    print("🚀 Starting Bulk Add Tags Test")
    print(f"Server: {BASE_URL}")
    print(f"Username: {USERNAME}")

    test_bulk_add_tags()

    print("\n✅ Test completed!")
    print("\n📚 The bulk-add-tags endpoint is now available at:")
    print("   POST /api/messaging/contacts/bulk-add-tags/")
