#!/usr/bin/env python
"""
Comprehensive API test for all endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from tenants.models import Tenant, Membership
from messaging.models import Contact
from messaging.models_sender_requests import SenderIDRequest
from billing.models import SMSBalance
import json

User = get_user_model()

def test_all_endpoints():
    """Test all API endpoints comprehensively"""
    
    print("=" * 60)
    print("COMPREHENSIVE API TEST")
    print("=" * 60)
    
    # Get or create test user
    user = User.objects.filter(email="normaluser@test.com").first()
    if not user:
        print("Test user not found. Please run test_normal_user_sms.py first.")
        return
    
    print(f"Using test user: {user.email}")
    
    # Get tenant
    tenant = user.tenant
    if not tenant:
        print("User has no tenant")
        return
    
    print(f"Using tenant: {tenant.name}")
    
    # Create test client
    client = Client()
    client.force_login(user)
    
    # Test 1: Contacts endpoint
    print("\n" + "=" * 40)
    print("TEST 1: CONTACTS ENDPOINT")
    print("=" * 40)
    
    try:
        # Test GET contacts
        response = client.get('/api/messaging/contacts/')
        print(f"GET /api/messaging/contacts/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"Success: Found {len(data)} contacts")
        else:
            print(f"Error: {response.content.decode()[:200]}")
            
        # Test POST contacts
        contact_data = {
            'name': 'Test Contact',
            'phone_e164': '+255700000001',
            'email': 'test@example.com'
        }
        
        response = client.post('/api/messaging/contacts/', 
                             data=json.dumps(contact_data),
                             content_type='application/json')
        print(f"POST /api/messaging/contacts/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = json.loads(response.content)
            print(f"Success: Created contact {data.get('id')}")
        else:
            print(f"Error: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"Exception in contacts test: {e}")
    
    # Test 2: Sender Requests endpoint
    print("\n" + "=" * 40)
    print("TEST 2: SENDER REQUESTS ENDPOINT")
    print("=" * 40)
    
    try:
        # Test GET sender requests
        response = client.get('/api/messaging/sender-requests/?page=1&page_size=10')
        print(f"GET /api/messaging/sender-requests/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"✅ Success: Found {len(data)} sender requests")
        else:
            print(f"❌ Error: {response.content.decode()[:200]}")
            
        # Test POST sender request
        request_data = {
            'request_type': 'custom',
            'requested_sender_id': 'TESTAPI',
            'sample_content': 'Test API content',
            'business_justification': 'Testing API functionality'
        }
        
        response = client.post('/api/messaging/sender-requests/',
                             data=json.dumps(request_data),
                             content_type='application/json')
        print(f"POST /api/messaging/sender-requests/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = json.loads(response.content)
            print(f"✅ Success: Created sender request {data.get('id')}")
        else:
            print(f"❌ Error: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"❌ Exception in sender requests test: {e}")
    
    # Test 3: Sender IDs endpoint
    print("\n" + "=" * 40)
    print("TEST 3: SENDER IDS ENDPOINT")
    print("=" * 40)
    
    try:
        # Test GET sender IDs
        response = client.get('/api/messaging/sender-ids/')
        print(f"GET /api/messaging/sender-ids/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"✅ Success: Found {len(data.get('data', []))} sender IDs")
        else:
            print(f"❌ Error: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"❌ Exception in sender IDs test: {e}")
    
    # Test 4: SMS Send endpoint
    print("\n" + "=" * 40)
    print("TEST 4: SMS SEND ENDPOINT")
    print("=" * 40)
    
    try:
        # Test SMS send
        sms_data = {
            'message': 'Test API SMS',
            'recipients': ['255700000001'],
            'sender_id': 'Taarifa-SMS'
        }
        
        response = client.post('/api/messaging/sms/send/',
                             data=json.dumps(sms_data),
                             content_type='application/json')
        print(f"POST /api/messaging/sms/send/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = json.loads(response.content)
            print(f"✅ Success: SMS sent - {data.get('message')}")
        else:
            print(f"❌ Error: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"❌ Exception in SMS send test: {e}")
    
    # Test 5: Admin interface
    print("\n" + "=" * 40)
    print("TEST 5: ADMIN INTERFACE")
    print("=" * 40)
    
    try:
        # Test admin SMSBalance page
        response = client.get('/admin/billing/smsbalance/')
        print(f"GET /admin/billing/smsbalance/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success: Admin SMSBalance page loads")
        else:
            print(f"❌ Error: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"❌ Exception in admin test: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_all_endpoints()
