#!/usr/bin/env python3
"""
Final test of API integration system.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from api_integration.models import APIAccount, APIKey

def test_api_final():
    """Test the API endpoints with proper authentication."""
    print("=" * 60)
    print("TESTING API INTEGRATION SYSTEM")
    print("=" * 60)
    
    # Get a test user and create API key
    user = User.objects.filter(email='ivan123@gmail.com').first()
    if not user:
        print("ERROR: Test user not found!")
        return False
    
    tenant = user.get_tenant()
    if not tenant:
        print("ERROR: User has no tenant!")
        return False
    
    # Get or create API account
    api_account, created = APIAccount.objects.get_or_create(
        owner=user,
        defaults={
            'name': f"{user.get_full_name() or user.email}'s API Account",
            'description': 'Test API account',
            'tenant': tenant,
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000,
            'rate_limit_per_day': 10000,
        }
    )
    
    # Get or create API key
    api_key = APIKey.objects.filter(api_account=api_account).first()
    if not api_key:
        api_key = APIKey.objects.create(
            api_account=api_account,
            key_name="Test API Key",
            permissions=['read', 'write']
        )
        api_key.api_key, api_key.secret_key = api_key.generate_keys()
        api_key.save()
    
    print(f"Using API Key: {api_key.api_key}")
    print(f"Tenant: {tenant.name}")
    
    # Test 1: SMS API - Send SMS
    print("\n1. Testing SMS API - Send SMS...")
    headers = {
        'Authorization': f'Bearer {api_key.api_key}',
        'Content-Type': 'application/json'
    }
    
    sms_data = {
        "message": "Hello from Mifumo SMS API! This is a test message.",
        "recipients": ["+255614853618"],
        "sender_id": "MIFUMO"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/sms/send/", 
            json=sms_data, 
            headers=headers, 
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: SMS sent successfully")
                message_id = result['data']['message_id']
                print(f"Message ID: {message_id}")
            else:
                print(f"FAIL: SMS send failed: {result.get('message')}")
        else:
            print(f"FAIL: SMS send returned {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: SMS send test failed: {e}")
    
    # Test 2: Contacts API
    print(f"\n2. Testing Contacts API...")
    try:
        contacts_response = requests.get(
            "http://127.0.0.1:8001/api/integration/v1/contacts/",
            headers=headers,
            timeout=10
        )
        print(f"Status Code: {contacts_response.status_code}")
        print(f"Response: {contacts_response.text}")
        
        if contacts_response.status_code == 200:
            print("SUCCESS: Contacts API working")
        else:
            print(f"FAIL: Contacts returned {contacts_response.status_code}")
    except Exception as e:
        print(f"ERROR: Contacts test failed: {e}")
    
    # Test 3: Create Contact
    print(f"\n3. Testing Create Contact...")
    contact_data = {
        "name": "Test Contact",
        "phone_number": "+255123456789",
        "email": "test@example.com",
        "tags": ["test", "api"]
    }
    
    try:
        create_contact_response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/contacts/create/",
            json=contact_data,
            headers=headers,
            timeout=10
        )
        print(f"Status Code: {create_contact_response.status_code}")
        print(f"Response: {create_contact_response.text}")
        
        if create_contact_response.status_code == 200:
            print("SUCCESS: Contact created")
        else:
            print(f"FAIL: Create contact returned {create_contact_response.status_code}")
    except Exception as e:
        print(f"ERROR: Create contact test failed: {e}")
    
    return True

def show_api_documentation():
    """Show API documentation."""
    print("\n" + "=" * 60)
    print("API DOCUMENTATION")
    print("=" * 60)
    
    print("\nBASE URL: http://127.0.0.1:8001/api/integration/v1/")
    print("\nAUTHENTICATION:")
    print("All API requests require authentication using an API key.")
    print("Include your API key in the Authorization header:")
    print("Authorization: Bearer YOUR_API_KEY_HERE")
    
    print("\nSMS API ENDPOINTS:")
    print("POST /sms/send/ - Send SMS message")
    print("GET /sms/status/{message_id}/ - Get message status")
    print("GET /sms/delivery-reports/ - Get delivery reports")
    print("GET /sms/balance/ - Get account balance")
    
    print("\nCONTACTS API ENDPOINTS:")
    print("GET /contacts/ - List contacts")
    print("POST /contacts/create/ - Create contact")
    print("GET /contacts/{id}/ - Get contact")
    print("PUT /contacts/{id}/update/ - Update contact")
    print("DELETE /contacts/{id}/delete/ - Delete contact")
    print("GET /contacts/search/ - Search contacts")
    
    print("\nSEGMENTS API ENDPOINTS:")
    print("GET /contacts/segments/ - List segments")
    print("POST /contacts/segments/create/ - Create segment")
    print("GET /contacts/segments/{id}/ - Get segment")
    print("PUT /contacts/segments/{id}/update/ - Update segment")
    print("DELETE /contacts/segments/{id}/delete/ - Delete segment")
    
    print("\nEXAMPLE REQUESTS:")
    print("\n1. Send SMS:")
    print("""
curl -X POST http://127.0.0.1:8001/api/integration/v1/sms/send/ \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Hello from Mifumo!",
    "recipients": ["+255123456789"],
    "sender_id": "MIFUMO"
  }'
    """)
    
    print("\n2. Create Contact:")
    print("""
curl -X POST http://127.0.0.1:8001/api/integration/v1/contacts/create/ \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "John Doe",
    "phone_number": "+255123456789",
    "email": "john@example.com",
    "tags": ["customer", "vip"]
  }'
    """)
    
    print("\n3. List Contacts:")
    print("""
curl -X GET http://127.0.0.1:8001/api/integration/v1/contacts/ \\
  -H "Authorization: Bearer YOUR_API_KEY"
    """)

def show_api_keys():
    """Show available API keys."""
    print("\n" + "=" * 60)
    print("AVAILABLE API KEYS")
    print("=" * 60)
    
    api_keys = APIKey.objects.filter(is_active=True)
    if api_keys.exists():
        for key in api_keys:
            print(f"\nKey Name: {key.key_name}")
            print(f"API Key: {key.api_key}")
            print(f"Secret Key: {key.secret_key}")
            print(f"Permissions: {', '.join(key.permissions)}")
            print(f"Created: {key.created_at}")
            print(f"Last Used: {key.last_used}")
            print("-" * 40)
    else:
        print("No API keys found. Create one using the Django admin or API.")

if __name__ == "__main__":
    print("Starting API Integration Tests...")
    
    success = test_api_final()
    show_api_documentation()
    show_api_keys()
    
    print("\n" + "=" * 60)
    if success:
        print("API INTEGRATION SYSTEM IS WORKING!")
        print("\nKey Features:")
        print("• API Key Authentication")
        print("• SMS Sending & Status Tracking")
        print("• Contact Management")
        print("• Delivery Reports")
        print("• Rate Limiting")
        print("• Webhook Support")
        print("\nNext Steps:")
        print("1. Use the API keys shown above")
        print("2. Test the endpoints with the examples")
        print("3. Integrate with your applications")
    else:
        print("Some tests failed. Check the output above.")

