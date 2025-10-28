#!/usr/bin/env python3
"""
Test API response to see what data is being returned.
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

def test_api_response():
    """Test API response to see the data structure."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing API Response Structure")
    print("=" * 50)
    
    # Setup test user
    print("\n1. Setting up test user...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="API Response Test Organization",
        defaults={
            'subdomain': 'api-response-test'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="apiresponse@example.com",
        defaults={
            'first_name': 'API',
            'last_name': 'Response User',
            'is_active': True
        }
    )
    
    # Set password for the user
    user.set_password('testpassword123')
    user.save()
    print(f"   User: {user.email} (ID: {user.id}) ({'created' if created else 'exists'})")
    
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
    
    # Test: Submit a sender request
    print("\n3. Submitting sender request...")
    
    timestamp = datetime.now().strftime("%H%M")
    submit_data = {
        "requested_sender_id": f"API{timestamp}",
        "sample_content": f"This is an API response test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    }
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=submit_data, headers=headers)
        print(f"   Submit Status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: Request submitted!")
                request_data = data.get('data', {})
                print(f"   Request ID: {request_data.get('id', 'N/A')}")
                print(f"   User ID in response: {request_data.get('user', 'N/A')}")
                print(f"   User ID field: {request_data.get('user_id', 'N/A')}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Submit failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test: Get sender requests list
    print("\n4. Testing sender requests list...")
    
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/?page=1&page_size=10", headers=headers)
        print(f"   List Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('data', {}).get('results', [])
                print(f"   SUCCESS: {len(results)} requests found")
                
                for i, req in enumerate(results):
                    print(f"   Request {i+1}:")
                    print(f"     ID: {req.get('id', 'N/A')}")
                    print(f"     Sender ID: {req.get('requested_sender_id', 'N/A')}")
                    print(f"     User: {req.get('user', 'N/A')}")
                    print(f"     User ID: {req.get('user_id', 'N/A')}")
                    print(f"     User Email: {req.get('user_email', 'N/A')}")
                    print(f"     Status: {req.get('status', 'N/A')}")
                    print(f"     Created: {req.get('created_at', 'N/A')}")
            else:
                print(f"   WARNING: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: List failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n5. API response test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_api_response()



















