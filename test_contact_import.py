#!/usr/bin/env python3
"""
Test Contact Import Endpoints
Tests CSV, Excel, and Mobile Phone Book import functionality
"""

import os
import sys
import django
import requests
import json
from io import StringIO

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from tenants.models import Tenant

def get_admin_user_and_token():
    """Get admin user and generate JWT token."""
    try:
        user = User.objects.get(email='admin@mifumo.com')
        refresh = RefreshToken.for_user(user)
        return user, str(refresh.access_token)
    except User.DoesNotExist:
        print("Admin user not found. Please create admin@mifumo.com user first.")
        return None, None

def test_csv_import():
    """Test CSV import endpoint."""
    print("=" * 80)
    print("TESTING CSV IMPORT")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/bulk-import/"
    
    # Test data matching the image format: name, phone, local_number
    csv_data = """name,phone,local_number,email,tags
John Mkumbo,+255672883530,672883530,john@example.com,vip
Fatma Mbwana,+255771978307,771978307,fatma@example.com,customer
Juma Shaaban,+255601709528,601709528,juma@example.com,regular
Gloria Kimaro,+255754865908,754865908,gloria@example.com,vip
Hassan Ndallahwa,+255766684630,766684630,hassan@example.com,customer"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "import_type": "csv",
        "csv_data": csv_data,
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

def test_excel_import():
    """Test Excel import endpoint."""
    print("\n" + "=" * 80)
    print("TESTING EXCEL IMPORT")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/bulk-import/"
    
    # Create a simple Excel file content (simulated)
    import pandas as pd
    from io import BytesIO
    
    # Create test data
    data = {
        'name': ['John Mkumbo', 'Fatma Mbwana', 'Juma Shaaban'],
        'phone': ['+255672883530', '+255771978307', '+255601709528'],
        'local_number': ['672883530', '771978307', '601709528'],
        'email': ['john@example.com', 'fatma@example.com', 'juma@example.com'],
        'tags': ['vip', 'customer', 'regular']
    }
    
    df = pd.DataFrame(data)
    
    # Convert to CSV for testing (since we can't easily create Excel file in test)
    csv_data = df.to_csv(index=False)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "import_type": "excel",
        "csv_data": csv_data,  # Using CSV data as Excel simulation
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

def test_mobile_phone_book_import():
    """Test mobile phone book import endpoint."""
    print("\n" + "=" * 80)
    print("TESTING MOBILE PHONE BOOK IMPORT")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/contacts/bulk-import/"
    
    # Simulate mobile phone book data
    contacts_data = [
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
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "import_type": "phone_contacts",
        "contacts": contacts_data,
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
    """Run all contact import tests."""
    print("Testing Contact Import Endpoints")
    print("=" * 80)
    
    # Test CSV import
    csv_result = test_csv_import()
    
    # Test Excel import
    excel_result = test_excel_import()
    
    # Test Mobile phone book import
    mobile_result = test_mobile_phone_book_import()
    
    # Test contact list
    list_result = test_contact_list()
    
    # Save results
    results = {
        "csv_import": csv_result,
        "excel_import": excel_result,
        "mobile_import": mobile_result,
        "contact_list": list_result
    }
    
    with open("contact_import_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("All test results saved to: contact_import_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
