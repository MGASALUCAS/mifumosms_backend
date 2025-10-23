#!/usr/bin/env python3
"""
Test Mobile Contact Import Endpoint
Tests direct mobile phone book import functionality
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

def get_admin_user_and_token():
    """Get admin user and generate JWT token."""
    try:
        user = User.objects.get(email='admin@mifumo.com')
        refresh = RefreshToken.for_user(user)
        return user, str(refresh.access_token)
    except User.DoesNotExist:
        print("Admin user not found. Please create admin@mifumo.com user first.")
        return None, None

def test_mobile_contact_import():
    """Test mobile contact import endpoint."""
    print("=" * 80)
    print("TESTING MOBILE CONTACT IMPORT")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/import/"
    
    # Simulate mobile contact picker data
    mobile_contacts = [
        {
            "full_name": "John Mkumbo",
            "phone": "+255672883530",
            "email": "john@example.com"
        },
        {
            "full_name": "Fatma Mbwana",
            "phone": "+255771978307",
            "email": "fatma@example.com"
        },
        {
            "full_name": "Juma Shaaban",
            "phone": "+255601709528",
            "email": "juma@example.com"
        },
        {
            "full_name": "Gloria Kimaro",
            "phone": "+255754865908",
            "email": "gloria@example.com"
        },
        {
            "full_name": "Hassan Ndallahwa",
            "phone": "+255766684630",
            "email": "hassan@example.com"
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contacts": mobile_contacts,
        "skip_duplicates": True,
        "update_existing": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_mobile_contact_import_with_duplicates():
    """Test mobile contact import with duplicate contacts."""
    print("\n" + "=" * 80)
    print("TESTING MOBILE CONTACT IMPORT WITH DUPLICATES")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/import/"
    
    # Try to import same contacts again (should be skipped)
    mobile_contacts = [
        {
            "full_name": "John Mkumbo",
            "phone": "+255672883530",
            "email": "john@example.com"
        },
        {
            "full_name": "Fatma Mbwana",
            "phone": "+255771978307",
            "email": "fatma@example.com"
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contacts": mobile_contacts,
        "skip_duplicates": True,
        "update_existing": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_contact_list():
    """Test contact list endpoint to see imported contacts."""
    print("\n" + "=" * 80)
    print("TESTING CONTACT LIST")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Run mobile contact import tests."""
    print("Testing Mobile Contact Import Endpoints")
    print("=" * 80)
    
    # Test mobile contact import
    mobile_result = test_mobile_contact_import()
    
    # Test mobile contact import with duplicates
    duplicate_result = test_mobile_contact_import_with_duplicates()
    
    # Test contact list
    list_result = test_contact_list()
    
    # Save results
    results = {
        "mobile_import": mobile_result,
        "duplicate_import": duplicate_result,
        "contact_list": list_result
    }
    
    with open("mobile_contact_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("All test results saved to: mobile_contact_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
