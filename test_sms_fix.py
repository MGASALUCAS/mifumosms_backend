#!/usr/bin/env python
"""
Test script to verify SMS functionality after fixing tenant access.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership

User = get_user_model()

def test_user_tenant_relationship():
    """Test that user has proper tenant relationship."""
    print("🔍 Testing User-Tenant Relationship...")
    
    try:
        user = User.objects.get(email='admin@mifumo.com')
        tenant = user.tenant
        
        print(f"✅ User: {user.email}")
        print(f"✅ Tenant: {tenant.name if tenant else 'None'}")
        print(f"✅ Tenant Subdomain: {tenant.subdomain if tenant else 'None'}")
        print(f"✅ Memberships: {user.memberships.count()}")
        
        if tenant:
            print("✅ User has valid tenant relationship!")
            return True
        else:
            print("❌ User has no tenant relationship!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing user-tenant relationship: {e}")
        return False

def test_sms_endpoint():
    """Test SMS endpoint with authentication."""
    print("\n🔍 Testing SMS Endpoint...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Step 1: Login to get JWT token
        print("📝 Step 1: Logging in...")
        login_data = {
            "email": "admin@mifumo.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{base_url}/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['tokens']['access']
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        # Step 2: Test SMS endpoint
        print("📝 Step 2: Testing SMS endpoint...")
        sms_data = {
            "message": "Test message from Mifumo WMS!",
            "recipients": ["255700000001"],
            "sender_id": "MIFUMO"
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        sms_response = requests.post(
            f"{base_url}/api/messaging/sms/sms/beem/send/",
            json=sms_data,
            headers=headers
        )
        
        print(f"📊 SMS Response Status: {sms_response.status_code}")
        print(f"📊 SMS Response: {sms_response.text}")
        
        if sms_response.status_code == 201:
            print("✅ SMS endpoint is working!")
            return True
        else:
            print("❌ SMS endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMS endpoint: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing SMS Fix...")
    print("=" * 50)
    
    # Test 1: User-Tenant Relationship
    tenant_ok = test_user_tenant_relationship()
    
    # Test 2: SMS Endpoint
    sms_ok = test_sms_endpoint()
    
    print("\n" + "=" * 50)
    if tenant_ok and sms_ok:
        print("🎉 All tests passed! SMS functionality is working!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 50)

if __name__ == '__main__':
    main()
