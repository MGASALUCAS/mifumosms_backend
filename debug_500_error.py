#!/usr/bin/env python3
"""
Debug the 500 error in sender request submission.
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
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def debug_500_error():
    """Debug the 500 error."""
    base_url = "http://127.0.0.1:8000"
    
    print("Debugging 500 Error")
    print("=" * 40)
    
    # Setup test user
    print("\n1. Setting up test user...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Debug 500 Error Organization",
        defaults={
            'subdomain': 'debug-500-error'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="debug500@example.com",
        defaults={
            'first_name': 'Debug',
            'last_name': '500 User',
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
    
    # Test: Try to reproduce the 500 error
    print("\n3. Testing sender request submission...")
    
    # Use the same data format that frontend might be sending
    submit_data = {
        "requested_sender_id": "DEBUG-TEST",
        "sample_content": "This is a debug test to reproduce the 500 error."
    }
    
    print(f"   Sending data: {json.dumps(submit_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 500:
            print(f"   ERROR: 500 Internal Server Error reproduced!")
            print(f"   Response body: {response.text}")
        elif response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: Sender request submitted!")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   UNEXPECTED: Status {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test: Check if there are any existing requests that might cause conflicts
    print("\n4. Checking for existing requests...")
    try:
        existing_requests = SenderIDRequest.objects.filter(tenant=tenant)
        print(f"   Existing requests: {existing_requests.count()}")
        for req in existing_requests:
            print(f"   - {req.requested_sender_id} ({req.status})")
    except Exception as e:
        print(f"   ERROR checking existing requests: {e}")
    
    print("\n5. Debug completed!")

if __name__ == "__main__":
    debug_500_error()


