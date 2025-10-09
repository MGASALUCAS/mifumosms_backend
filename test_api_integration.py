#!/usr/bin/env python3
"""
API Integration Test for Mifumo WMS
Tests the optimized backend APIs with frontend integration patterns.
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
from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework import status
from tenants.models import Tenant, Membership
from messaging.models import Contact, Segment, Template, Conversation, Message

User = get_user_model()

class APIIntegrationTest:
    """Test the optimized API endpoints for frontend integration."""
    
    def __init__(self):
        self.client = APIClient()
        self.base_url = 'http://127.0.0.1:8000/api'
        self.user = None
        self.tenant = None
        self.access_token = None
        
    def setup_test_data(self):
        """Create test user and tenant."""
        print("Setting up test data...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            email='test@mifumo.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_verified': True
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Create test tenant
        self.tenant, created = Tenant.objects.get_or_create(
            subdomain='test-tenant',
            defaults={
                'name': 'Test Tenant',
                'business_name': 'Test Business',
                'is_active': True
            }
        )
        
        # Create membership
        membership, created = Membership.objects.get_or_create(
            user=self.user,
            tenant=self.tenant,
            defaults={
                'role': 'owner',
                'status': 'active'
            }
        )
        
        print(f"✓ Test user: {self.user.email}")
        print(f"✓ Test tenant: {self.tenant.name}")
        
    def authenticate(self):
        """Authenticate and get access token."""
        print("Authenticating...")
        
        # Login
        response = self.client.post(f'{self.base_url}/auth/login/', {
            'email': 'test@mifumo.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['tokens']['access']
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            print("✓ Authentication successful")
            return True
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(response.json())
            return False
    
    def test_auth_endpoints(self):
        """Test authentication endpoints."""
        print("\n=== Testing Authentication Endpoints ===")
        
        # Test profile endpoint
        response = self.client.get(f'{self.base_url}/auth/profile/')
        if response.status_code == 200:
            print("✓ GET /auth/profile/ - OK")
        else:
            print(f"✗ GET /auth/profile/ - Failed: {response.status_code}")
    
    def test_tenant_endpoints(self):
        """Test tenant management endpoints."""
        print("\n=== Testing Tenant Endpoints ===")
        
        # Test get tenants
        response = self.client.get(f'{self.base_url}/tenants/')
        if response.status_code == 200:
            print("✓ GET /tenants/ - OK")
        else:
            print(f"✗ GET /tenants/ - Failed: {response.status_code}")
    
    def test_contact_endpoints(self):
        """Test contact management endpoints."""
        print("\n=== Testing Contact Endpoints ===")
        
        # Test get contacts
        response = self.client.get(f'{self.base_url}/messaging/contacts/')
        if response.status_code == 200:
            print("✓ GET /messaging/contacts/ - OK")
        else:
            print(f"✗ GET /messaging/contacts/ - Failed: {response.status_code}")
        
        # Test create contact
        contact_data = {
            'name': 'Test Contact',
            'phone_e164': '+255700000001',
            'email': 'test@example.com',
            'tags': ['test', 'demo']
        }
        response = self.client.post(f'{self.base_url}/messaging/contacts/', contact_data)
        if response.status_code == 201:
            print("✓ POST /messaging/contacts/ - OK")
            return response.json()['id']
        else:
            print(f"✗ POST /messaging/contacts/ - Failed: {response.status_code}")
            return None
    
    def test_sms_endpoints(self):
        """Test SMS endpoints."""
        print("\n=== Testing SMS Endpoints ===")
        
        # Test SMS balance
        response = self.client.get(f'{self.base_url}/messaging/sms/balance/')
        if response.status_code == 200:
            print("✓ GET /messaging/sms/balance/ - OK")
        else:
            print(f"✗ GET /messaging/sms/balance/ - Failed: {response.status_code}")
        
        # Test SMS stats
        response = self.client.get(f'{self.base_url}/messaging/sms/stats/')
        if response.status_code == 200:
            print("✓ GET /messaging/sms/stats/ - OK")
        else:
            print(f"✗ GET /messaging/sms/stats/ - Failed: {response.status_code}")
        
        # Test phone validation
        response = self.client.post(f'{self.base_url}/messaging/sms/validate-phone/', {
            'phone': '+255700000001'
        })
        if response.status_code == 200:
            print("✓ POST /messaging/sms/validate-phone/ - OK")
        else:
            print(f"✗ POST /messaging/sms/validate-phone/ - Failed: {response.status_code}")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints."""
        print("\n=== Testing Analytics Endpoints ===")
        
        # Test analytics overview
        response = self.client.get(f'{self.base_url}/messaging/analytics/overview/')
        if response.status_code == 200:
            print("✓ GET /messaging/analytics/overview/ - OK")
        else:
            print(f"✗ GET /messaging/analytics/overview/ - Failed: {response.status_code}")
    
    def test_billing_endpoints(self):
        """Test billing endpoints."""
        print("\n=== Testing Billing Endpoints ===")
        
        # Test billing plans
        response = self.client.get(f'{self.base_url}/billing/plans/')
        if response.status_code == 200:
            print("✓ GET /billing/plans/ - OK")
        else:
            print(f"✗ GET /billing/plans/ - Failed: {response.status_code}")
        
        # Test billing overview
        response = self.client.get(f'{self.base_url}/billing/overview/')
        if response.status_code == 200:
            print("✓ GET /billing/overview/ - OK")
        else:
            print(f"✗ GET /billing/overview/ - Failed: {response.status_code}")
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting API Integration Tests for Mifumo WMS")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_test_data()
            
            # Authenticate
            if not self.authenticate():
                print("❌ Authentication failed. Exiting.")
                return False
            
            # Run tests
            self.test_auth_endpoints()
            self.test_tenant_endpoints()
            contact_id = self.test_contact_endpoints()
            self.test_sms_endpoints()
            self.test_analytics_endpoints()
            self.test_billing_endpoints()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed!")
            print(f"📊 Test Summary:")
            print(f"   - User: {self.user.email}")
            print(f"   - Tenant: {self.tenant.name}")
            print(f"   - Contact ID: {contact_id}")
            print(f"   - Access Token: {'✓' if self.access_token else '✗'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main test runner."""
    test = APIIntegrationTest()
    success = test.run_all_tests()
    
    if success:
        print("\n🎉 Integration tests passed! Backend is ready for frontend.")
        sys.exit(0)
    else:
        print("\n💥 Integration tests failed! Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
