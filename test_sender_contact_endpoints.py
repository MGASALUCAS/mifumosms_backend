#!/usr/bin/env python3
"""
Test script for sender ID request and contact endpoints.
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
from billing.models import SMSBalance, SMSPackage
from messaging.models import Contact, SMSSenderID
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def test_sender_contact_endpoints():
    """Test sender ID request and contact endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Sender ID Request and Contact Endpoints")
    print("=" * 60)
    
    # Test data setup
    print("\n1. Setting up test data...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Sender Contact Organization",
        defaults={
            'subdomain': 'test-sender-contact'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="test-sender-contact@example.com",
        defaults={
            'first_name': 'Test',
            'last_name': 'Sender Contact User',
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
    
    # Create SMS balance
    sms_balance, created = SMSBalance.objects.get_or_create(tenant=tenant)
    print(f"   SMS Balance: {sms_balance.credits} credits ({'created' if created else 'exists'})")
    
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
            print(f"   Response: {auth_response.text}")
            return
    except Exception as e:
        print(f"   Auth error: {e}")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    print("\n3. Testing sender ID and contact endpoints...")
    
    # Test sender IDs list
    print("\n   Testing sender IDs list...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-ids/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Sender IDs Count: {len(data.get('data', []))}")
                print(f"   Response: {data}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test sender ID request
    print("\n   Testing sender ID request...")
    try:
        request_data = {
            "requested_sender_id": "Test-SMS",
            "business_name": "Test Business",
            "business_type": "Technology",
            "contact_person": "John Doe",
            "contact_phone": "0744963858",
            "contact_email": "test@example.com",
            "business_license": "LIC123456",
            "purpose": "Customer notifications"
        }
        response = requests.post(f"{base_url}/api/messaging/sender-ids/request/", 
                               json=request_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Sender ID Request: {data.get('message', 'N/A')}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test sender requests list
    print("\n   Testing sender requests list...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-requests/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Sender Requests Count: {len(data.get('data', []))}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test contacts list
    print("\n   Testing contacts list...")
    try:
        response = requests.get(f"{base_url}/api/messaging/contacts/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Contacts Count: {len(data.get('data', []))}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test contact creation
    print("\n   Testing contact creation...")
    try:
        contact_data = {
            "name": "Test Contact 2",
            "phone_e164": "+255757347864",
            "email": "contact2@example.com",
            "tags": ["test", "customer"]
        }
        response = requests.post(f"{base_url}/api/messaging/contacts/", 
                               json=contact_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print(f"   Contact Created: {data.get('data', {}).get('id', 'N/A')}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test default sender ID request
    print("\n   Testing default sender ID request...")
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/request-default/", 
                               headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Default Sender ID Request: {data.get('message', 'N/A')}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Sender ID and Contact endpoints test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_sender_contact_endpoints()
