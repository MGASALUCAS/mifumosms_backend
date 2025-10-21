#!/usr/bin/env python3
"""
Test correct submit endpoint with proper data format.
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

def test_correct_submit():
    """Test submit endpoint with correct data format."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Correct Submit Endpoint")
    print("=" * 40)
    
    # Setup test user
    print("\n1. Setting up test user...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Correct Submit Test Organization",
        defaults={
            'subdomain': 'correct-submit-test'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="correctsubmit@example.com",
        defaults={
            'first_name': 'Correct',
            'last_name': 'Submit User',
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
    
    # Test submit endpoint with correct data
    print("\n3. Testing submit endpoint with correct data...")
    
    # Correct data format based on serializer requirements
    submit_data = {
        "request_type": "custom",  # or "default"
        "requested_sender_id": "TEST-SMS",
        "sample_content": "This is a test message for sender ID validation.",
        "business_justification": "We need this sender ID for testing our SMS functionality and validating our messaging system."
    }
    
    print(f"   Sending data: {json.dumps(submit_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: Sender request submitted!")
                request_data = data.get('data', {})
                print(f"   Request ID: {request_data.get('id', 'N/A')}")
                print(f"   Status: {request_data.get('status', 'N/A')}")
                print(f"   Sender ID: {request_data.get('requested_sender_id', 'N/A')}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Submit failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test stats endpoint after submission
    print("\n4. Testing stats endpoint after submission...")
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
                print(f"   Approved: {stats.get('approved_requests', 0)}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Stats endpoint failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n5. Correct submit test completed!")
    print("=" * 40)
    print("FRONTEND INTEGRATION GUIDE:")
    print("=" * 40)
    print("Required fields for POST /api/messaging/sender-requests/submit/:")
    print("- request_type: 'custom' or 'default'")
    print("- requested_sender_id: string (max 11 chars)")
    print("- sample_content: string (max 170 chars)")
    print("- business_justification: string (required)")
    print("=" * 40)

if __name__ == "__main__":
    test_correct_submit()

