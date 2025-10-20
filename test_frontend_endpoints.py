#!/usr/bin/env python3
"""
Test frontend endpoints to debug issues.
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
from messaging.models import Contact
from messaging.models_sms import SMSSenderID, SMSProvider
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def test_frontend_endpoints():
    """Test frontend endpoints to debug issues."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Frontend Endpoints")
    print("=" * 50)
    
    # Setup test user
    print("\n1. Setting up test user...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Frontend Test Organization",
        defaults={
            'subdomain': 'frontend-test'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="frontendtest@example.com",
        defaults={
            'first_name': 'Frontend',
            'last_name': 'Test User',
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
    
    # Test stats endpoint
    print("\n3. Testing sender requests stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/stats/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {}).get('stats', {})
                print(f"   SUCCESS: Stats retrieved!")
                print(f"   Total Requests: {stats.get('total_requests', 0)}")
                print(f"   Pending: {stats.get('pending_requests', 0)}")
                print(f"   Approved: {stats.get('approved_requests', 0)}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Stats endpoint failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test submit endpoint with different data formats
    print("\n4. Testing sender request submit endpoint...")
    
    # Test data 1: Minimal data
    print("\n   a) Testing with minimal data...")
    try:
        submit_data = {
            "requested_sender_id": "TEST-SMS",
            "sample_content": "This is a test message for sender ID validation."
        }
        
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"      SUCCESS: Sender request submitted!")
            else:
                print(f"      WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"      ERROR: Submit failed with status: {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # Test data 2: Full data
    print("\n   b) Testing with full data...")
    try:
        submit_data = {
            "requested_sender_id": "FULL-TEST",
            "sample_content": "This is a comprehensive test message for sender ID validation with full data.",
            "business_name": "Test Business",
            "business_type": "Technology",
            "contact_person": "Test Person",
            "contact_phone": "+255700000000",
            "contact_email": "test@example.com",
            "purpose": "Testing and validation",
            "expected_volume": 1000,
            "compliance_agreement": True
        }
        
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"      SUCCESS: Sender request submitted!")
            else:
                print(f"      WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"      ERROR: Submit failed with status: {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # Test data 3: Invalid data to see validation errors
    print("\n   c) Testing with invalid data...")
    try:
        submit_data = {
            "requested_sender_id": "",  # Empty sender ID
            "sample_content": ""  # Empty content
        }
        
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"      EXPECTED: Validation errors - {data.get('errors', {})}")
        else:
            print(f"      UNEXPECTED: Status {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # Test regular sender requests endpoint for comparison
    print("\n5. Testing regular sender requests endpoint...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                requests_list = data.get('data', [])
                print(f"   SUCCESS: {len(requests_list)} requests found")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Regular endpoint failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n6. Frontend endpoints test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_frontend_endpoints()
