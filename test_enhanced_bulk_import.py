#!/usr/bin/env python3
"""
Test script for enhanced bulk import functionality.
This script tests the new unified bulk import endpoint without requiring a running server.
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')

import django
django.setup()

from messaging.serializers import ContactBulkImportSerializer
from messaging.views import ContactBulkImportView
from accounts.models import User
from tenants.models import Tenant

def test_csv_import_serializer():
    """Test CSV import serializer validation."""
    print("Testing CSV Import Serializer...")
    
    # Valid CSV data
    valid_data = {
        "import_type": "csv",
        "csv_data": "name,phone_e164,email,tags\nJohn Doe,+255700000001,john@example.com,vip,customer\nJane Smith,+255700000002,jane@example.com,regular",
        "skip_duplicates": True,
        "update_existing": False
    }
    
    serializer = ContactBulkImportSerializer(data=valid_data)
    if serializer.is_valid():
        print("✓ CSV serializer validation passed")
        return True
    else:
        print(f"✗ CSV serializer validation failed: {serializer.errors}")
        return False

def test_phone_contacts_serializer():
    """Test phone contacts import serializer validation."""
    print("Testing Phone Contacts Import Serializer...")
    
    # Valid phone contacts data
    valid_data = {
        "import_type": "phone_contacts",
        "contacts": [
            {
                "full_name": "John Doe",
                "phone": "+255700000001",
                "email": "john@example.com"
            },
            {
                "full_name": "Jane Smith",
                "phone": "255700000002",  # Test normalization
                "email": "jane@example.com"
            }
        ],
        "skip_duplicates": True,
        "update_existing": False
    }
    
    serializer = ContactBulkImportSerializer(data=valid_data)
    if serializer.is_valid():
        print("✓ Phone contacts serializer validation passed")
        # Test phone normalization
        contacts = serializer.validated_data['contacts']
        if contacts[1]['phone'] == '+255700000002':
            print("✓ Phone number normalization working")
        else:
            print(f"✗ Phone number normalization failed: {contacts[1]['phone']}")
        return True
    else:
        print(f"✗ Phone contacts serializer validation failed: {serializer.errors}")
        return False

def test_invalid_data():
    """Test serializer with invalid data."""
    print("Testing Invalid Data Handling...")
    
    # Invalid data - missing required fields
    invalid_data = {
        "import_type": "csv",
        "csv_data": "name,email\nJohn Doe,john@example.com",  # Missing phone_e164
        "skip_duplicates": True,
        "update_existing": False
    }
    
    serializer = ContactBulkImportSerializer(data=invalid_data)
    if not serializer.is_valid():
        print("✓ Invalid data correctly rejected")
        return True
    else:
        print("✗ Invalid data was accepted")
        return False

def test_phone_normalization():
    """Test phone number normalization."""
    print("Testing Phone Number Normalization...")
    
    test_cases = [
        ("255700000001", "+255700000001"),
        ("0700000001", "+255700000001"),
        ("+255700000001", "+255700000001"),
        ("1234567890", "+1234567890"),
        ("", ""),
    ]
    
    serializer = ContactBulkImportSerializer()
    
    for input_phone, expected in test_cases:
        result = serializer._normalize_phone(input_phone)
        if result == expected:
            print(f"✓ {input_phone} → {result}")
        else:
            print(f"✗ {input_phone} → {result} (expected {expected})")
            return False
    
    return True

def test_import_type_validation():
    """Test import type validation."""
    print("Testing Import Type Validation...")
    
    # Test missing data for CSV
    csv_data = {
        "import_type": "csv",
        "skip_duplicates": True,
        "update_existing": False
        # Missing csv_data
    }
    
    serializer = ContactBulkImportSerializer(data=csv_data)
    if not serializer.is_valid():
        print("✓ Missing CSV data correctly rejected")
    else:
        print("✗ Missing CSV data was accepted")
        return False
    
    # Test missing data for phone contacts
    phone_data = {
        "import_type": "phone_contacts",
        "skip_duplicates": True,
        "update_existing": False
        # Missing contacts
    }
    
    serializer = ContactBulkImportSerializer(data=phone_data)
    if not serializer.is_valid():
        print("✓ Missing phone contacts data correctly rejected")
    else:
        print("✗ Missing phone contacts data was accepted")
        return False
    
    return True

def test_contact_validation():
    """Test contact data validation."""
    print("Testing Contact Data Validation...")
    
    # Test contact with no name or phone
    invalid_contact_data = {
        "import_type": "phone_contacts",
        "contacts": [
            {
                "email": "test@example.com"
                # Missing full_name and phone
            }
        ],
        "skip_duplicates": True,
        "update_existing": False
    }
    
    serializer = ContactBulkImportSerializer(data=invalid_contact_data)
    if not serializer.is_valid():
        print("✓ Contact without name or phone correctly rejected")
    else:
        print("✗ Contact without name or phone was accepted")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Bulk Import Functionality")
    print("=" * 50)
    
    tests = [
        test_csv_import_serializer,
        test_phone_contacts_serializer,
        test_invalid_data,
        test_phone_normalization,
        test_import_type_validation,
        test_contact_validation,
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
        print("🎉 All tests passed! Enhanced bulk import is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
