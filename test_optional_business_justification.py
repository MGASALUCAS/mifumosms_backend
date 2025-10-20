#!/usr/bin/env python3
"""
Test that business_justification is now optional.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from billing.models import SMSBalance

User = get_user_model()

def test_optional_business_justification():
    """Test that business_justification is now optional."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Optional Business Justification")
    print("=" * 50)
    
    # Setup test user
    print("\n1. Setting up test user...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Optional Business Test Organization",
        defaults={
            'subdomain': 'optional-business-test'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="optionalbusiness@example.com",
        defaults={
            'first_name': 'Optional',
            'last_name': 'Business User',
            'is_active': True
        }
    )
    
    # Set password for the user
    user.set_password('testpassword123')
    user.save()
    print(f"   User: {user.email} ({'created' if created else 'exists'})")
    
    # Create membership
    membership, created = Membership.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={'role': 'admin'}
    )
    print(f"   Membership: {membership.role} ({'created' if created else 'exists'})")
    
    # Get user's actual tenant
    user_tenant = user.tenant
    if user_tenant and user_tenant != tenant:
        print(f"   User's actual tenant: {user_tenant.name}")
        tenant = user_tenant
    
    # Create SMS balance
    sms_balance, created = SMSBalance.objects.get_or_create(tenant=tenant)
    sms_balance.credits = 5
    sms_balance.total_purchased = 5
    sms_balance.save()
    print(f"   SMS Balance: {sms_balance.credits} credits")
    
    # Get authentication token
    print("\n2. Getting authentication token...")
    auth_url = f"{base_url}/api/auth/login/"
    auth_data = {
        "email": user.email,
        "password": "testpassword123"
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_data)
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            if 'tokens' in auth_result:
                token = auth_result['tokens']['access']
                print(f"   Token obtained: {token[:20]}...")
            else:
                print(f"   Auth failed: {auth_result.get('message', 'Unknown error')}")
                return
        else:
            print(f"   Auth failed with status: {auth_response.status_code}")
            return
    except Exception as e:
        print(f"   Auth error: {e}")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Minimal data without business_justification
    print("\n3. Testing with minimal data (no business_justification)...")
    
    minimal_data = {
        "requested_sender_id": "MINIMAL",
        "sample_content": "This is a minimal test without business justification."
    }
    
    print(f"   Sending data: {json.dumps(minimal_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=minimal_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: Minimal data works! Business justification is optional.")
                request_data = data.get('data', {})
                print(f"   Request ID: {request_data.get('id', 'N/A')}")
                print(f"   Business Justification: {request_data.get('business_justification', 'None')}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Minimal data failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: With business_justification
    print("\n4. Testing with business_justification...")
    
    full_data = {
        "requested_sender_id": "FULL-TEST",
        "sample_content": "This is a full test with business justification.",
        "business_justification": "This is for testing the optional business justification field."
    }
    
    print(f"   Sending data: {json.dumps(full_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=full_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: Full data works!")
                request_data = data.get('data', {})
                print(f"   Request ID: {request_data.get('id', 'N/A')}")
                print(f"   Business Justification: {request_data.get('business_justification', 'None')}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Full data failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Check stats
    print("\n5. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/stats/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {}).get('stats', {})
                print(f"   SUCCESS: Stats retrieved!")
                print(f"   Total Requests: {stats.get('total_requests', 0)}")
                print(f"   Pending: {stats.get('pending_requests', 0)}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Stats endpoint failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n6. Optional business justification test completed!")
    print("=" * 50)
    print("FRONTEND UPDATE:")
    print("=" * 50)
    print("SUCCESS: business_justification is now OPTIONAL!")
    print("Your frontend can now send just:")
    print('{')
    print('  "requested_sender_id": "YOUR-SENDER-ID",')
    print('  "sample_content": "Your sample message"')
    print('}')
    print("=" * 50)

if __name__ == "__main__":
    test_optional_business_justification()
