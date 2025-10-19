#!/usr/bin/env python3
"""
Test script for the new submit sender request endpoint.
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership

User = get_user_model()

def test_submit_endpoint():
    """Test the new submit sender request endpoint."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Submit Sender Request Endpoint")
    print("=" * 50)
    
    # Test data setup
    print("\n1. Setting up test data...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Submit Organization",
        defaults={
            'subdomain': 'test-submit'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="test-submit@example.com",
        defaults={
            'first_name': 'Test',
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
    
    # Test the submit endpoint
    print("\n3. Testing submit sender request endpoint...")
    try:
        request_data = {
            "requested_sender_id": "TestSubmit",
            "sample_content": "A test use case for the sender name purposely used for information transfer.",
            "business_justification": "Requesting to use this sender ID for customer notifications and business communications.",
            "business_name": "Test Submit Business",
            "business_type": "Technology",
            "contact_person": "John Doe",
            "contact_phone": "0744963858",
            "contact_email": "test@example.com",
            "business_license": "LIC123456"
        }
        
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=request_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success') or 'id' in data:
                print(f"   SUCCESS: Submit endpoint working correctly!")
                print(f"   Sender ID Request: {data.get('requested_sender_id', 'N/A')}")
            else:
                print(f"   WARNING: Response indicates error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Submit endpoint failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: Error testing submit endpoint: {e}")
    
    # Test the regular endpoint for comparison
    print("\n4. Testing regular sender request endpoint for comparison...")
    try:
        request_data = {
            "requested_sender_id": "TestReg",
            "sample_content": "A test use case for the sender name purposely used for information transfer.",
            "business_justification": "Requesting to use this sender ID for customer notifications and business communications.",
            "business_name": "Test Regular Business",
            "business_type": "Technology",
            "contact_person": "Jane Doe",
            "contact_phone": "0744963859",
            "contact_email": "jane@example.com",
            "business_license": "LIC123457"
        }
        
        response = requests.post(f"{base_url}/api/messaging/sender-requests/", 
                               json=request_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success') or 'id' in data:
                print(f"   SUCCESS: Regular endpoint working correctly!")
            else:
                print(f"   WARNING: Response indicates error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Regular endpoint failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: Error testing regular endpoint: {e}")
    
    print("\n5. Submit endpoint test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_submit_endpoint()
