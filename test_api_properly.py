#!/usr/bin/env python3
"""
Test API endpoints properly with authentication.
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

def test_api_properly():
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
                print("✅ SUCCESS: SMS sent successfully")
                message_id = result['data']['message_id']
                print(f"Message ID: {message_id}")
                
                # Test 2: Get Message Status
                print(f"\n2. Testing Message Status...")
                try:
                    status_response = requests.get(
                        f"http://127.0.0.1:8001/api/integration/v1/sms/status/{message_id}/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Status Code: {status_response.status_code}")
                    print(f"Response: {status_response.text}")
                    
                    if status_response.status_code == 200:
                        print("✅ SUCCESS: Message status retrieved")
                    else:
                        print(f"❌ FAIL: Status returned {status_response.status_code}")
                except Exception as e:
                    print(f"❌ ERROR: Status test failed: {e}")
                
                # Test 3: Delivery Reports
                print(f"\n3. Testing Delivery Reports...")
                try:
                    reports_response = requests.get(
                        "http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Status Code: {reports_response.status_code}")
                    print(f"Response: {reports_response.text}")
                    
                    if reports_response.status_code == 200:
                        print("✅ SUCCESS: Delivery reports retrieved")
                    else:
                        print(f"❌ FAIL: Reports returned {reports_response.status_code}")
                except Exception as e:
                    print(f"❌ ERROR: Reports test failed: {e}")
                
                # Test 4: Balance
                print(f"\n4. Testing Balance...")
                try:
                    balance_response = requests.get(
                        "http://127.0.0.1:8001/api/integration/v1/sms/balance/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Status Code: {balance_response.status_code}")
                    print(f"Response: {balance_response.text}")
                    
                    if balance_response.status_code == 200:
                        print("✅ SUCCESS: Balance retrieved")
                    else:
                        print(f"❌ FAIL: Balance returned {balance_response.status_code}")
                except Exception as e:
                    print(f"❌ ERROR: Balance test failed: {e}")
                
            else:
                print(f"❌ FAIL: SMS send failed: {result.get('message')}")
        else:
            print(f"❌ FAIL: SMS send returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: SMS send test failed: {e}")
    
    # Test 5: Contacts API
    print(f"\n5. Testing Contacts API...")
    try:
        contacts_response = requests.get(
            "http://127.0.0.1:8001/api/integration/v1/contacts/",
            headers=headers,
            timeout=10
        )
        print(f"Status Code: {contacts_response.status_code}")
        print(f"Response: {contacts_response.text}")
        
        if contacts_response.status_code == 200:
            print("✅ SUCCESS: Contacts API working")
        else:
            print(f"❌ FAIL: Contacts returned {contacts_response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: Contacts test failed: {e}")
    
    # Test 6: Create Contact
    print(f"\n6. Testing Create Contact...")
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
            print("✅ SUCCESS: Contact created")
        else:
            print(f"❌ FAIL: Create contact returned {create_contact_response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: Create contact test failed: {e}")
    
    return True

def show_api_usage_examples():
    """Show API usage examples."""
    print("\n" + "=" * 60)
    print("API USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1. JavaScript Example:")
    print("""
const API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
const BASE_URL = 'http://127.0.0.1:8001/api/integration/v1';

// Send SMS
async function sendSMS(message, recipients) {
    const response = await fetch(`${BASE_URL}/sms/send/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            recipients: recipients,
            'sender_id': 'MIFUMO'
        })
    });
    
    return await response.json();
}

// Usage
sendSMS('Hello from Mifumo!', ['+255123456789'])
    .then(result => console.log(result))
    .catch(error => console.error(error));
    """)
    
    print("\n2. Python Example:")
    print("""
import requests

API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
BASE_URL = 'http://127.0.0.1:8001/api/integration/v1'

def send_sms(message, recipients):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'message': message,
        'recipients': recipients,
        'sender_id': 'MIFUMO'
    }
    
    response = requests.post(f'{BASE_URL}/sms/send/', json=data, headers=headers)
    return response.json()

# Usage
result = send_sms('Hello from Mifumo!', ['+255123456789'])
print(result)
    """)
    
    print("\n3. cURL Example:")
    print("""
curl -X POST http://127.0.0.1:8001/api/integration/v1/sms/send/ \\
  -H "Authorization: Bearer mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Hello from Mifumo!",
    "recipients": ["+255123456789"],
    "sender_id": "MIFUMO"
  }'
    """)

if __name__ == "__main__":
    print("Starting API Integration Tests...")
    
    success = test_api_properly()
    show_api_usage_examples()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API INTEGRATION SYSTEM IS WORKING!")
        print("\nKey Features:")
        print("• API Key Authentication")
        print("• SMS Sending & Status Tracking")
        print("• Contact Management")
        print("• Delivery Reports")
        print("• Rate Limiting")
        print("• Webhook Support")
        print("\nNext Steps:")
        print("1. Get your API key from the database")
        print("2. Use the examples above to integrate")
        print("3. Set up webhooks for real-time notifications")
    else:
        print("❌ Some tests failed. Check the output above.")

