#!/usr/bin/env python
"""
Simple API test for all endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from tenants.models import Tenant, Membership
import json

User = get_user_model()

def test_all_endpoints():
    """Test all API endpoints"""
    
    print("=" * 60)
    print("API ENDPOINT TEST")
    print("=" * 60)
    
    # Get test user
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
            print(f"SUCCESS: Found {len(data)} contacts")
        else:
            print(f"ERROR: {response.content.decode()[:200]}")
            
        # Test POST contacts
        contact_data = {
            'name': 'Test Contact API',
            'phone_e164': '+255700000002',
            'email': 'testapi@example.com'
        }
        
        response = client.post('/api/messaging/contacts/', 
                             data=json.dumps(contact_data),
                             content_type='application/json')
        print(f"POST /api/messaging/contacts/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            data = json.loads(response.content)
            print(f"SUCCESS: Created contact {data.get('id')}")
        else:
            print(f"ERROR: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION in contacts test: {e}")
    
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
            print(f"SUCCESS: Found {len(data)} sender requests")
        else:
            print(f"ERROR: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION in sender requests test: {e}")
    
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
            print(f"SUCCESS: Found {len(data.get('data', []))} sender IDs")
        else:
            print(f"ERROR: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION in sender IDs test: {e}")
    
    # Test 4: Admin interface
    print("\n" + "=" * 40)
    print("TEST 4: ADMIN INTERFACE")
    print("=" * 40)
    
    try:
        # Test admin SMSBalance page
        response = client.get('/admin/billing/smsbalance/')
        print(f"GET /admin/billing/smsbalance/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Admin SMSBalance page loads")
        else:
            print(f"ERROR: {response.content.decode()[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION in admin test: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_all_endpoints()
