#!/usr/bin/env python3
"""
Test script for dashboard endpoints to verify data fetching from database
"""
import requests
import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from messaging.models import Contact, Message, Campaign, Conversation
from messaging.models_sms import SMSMessage, SMSDeliveryReport
from tenants.models import Tenant
from billing.models import SMSBalance, SMSPackage

User = get_user_model()

def get_admin_user_and_token():
    """Get admin user and return JWT token"""
    try:
        # Get the admin user
        user = User.objects.get(email='admin@mifumo.com')
        
        # Get user's tenant
        tenant = user.get_tenant()
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"Found admin user: {user.email}")
        print(f"User tenant: {tenant.name if tenant else 'No tenant'}")
        print(f"Generated JWT token")
        
        return access_token, user, tenant
        
    except User.DoesNotExist:
        print(f"Admin user admin@mifumo.com not found. Please create it first.")
        return None, None, None
    except Exception as e:
        print(f"Error getting admin user: {e}")
        return None, None, None

def create_test_data(tenant):
    """Create some test data in the database"""
    try:
        print("\nCreating test data...")
        
        # Create test contacts
        contact1, created = Contact.objects.get_or_create(
            phone_number='+255700000001',
            tenant=tenant,
            defaults={
                'name': 'John Kamau',
                'email': 'john@example.com'
            }
        )
        
        contact2, created = Contact.objects.get_or_create(
            phone_number='+255700000002',
            tenant=tenant,
            defaults={
                'name': 'Sarah Mwangi',
                'email': 'sarah@example.com'
            }
        )
        
        # Create test messages
        message1, created = Message.objects.get_or_create(
            content='Test message 1',
            recipient=contact1,
            tenant=tenant,
            defaults={
                'status': 'delivered',
                'message_type': 'sms'
            }
        )
        
        message2, created = Message.objects.get_or_create(
            content='Test message 2',
            recipient=contact2,
            tenant=tenant,
            defaults={
                'status': 'delivered',
                'message_type': 'whatsapp'
            }
        )
        
        # Create test campaign
        campaign, created = Campaign.objects.get_or_create(
            name='Welcome Campaign',
            tenant=tenant,
            defaults={
                'status': 'completed',
                'message_type': 'whatsapp',
                'total_recipients': 100,
                'sent_count': 100,
                'delivered_count': 98
            }
        )
        
        # Create test conversation
        conversation, created = Conversation.objects.get_or_create(
            contact=contact1,
            tenant=tenant,
            defaults={
                'status': 'active',
                'last_message': 'Test conversation'
            }
        )
        
        print(f"Created {Contact.objects.filter(tenant=tenant).count()} contacts")
        print(f"Created {Message.objects.filter(tenant=tenant).count()} messages")
        print(f"Created {Campaign.objects.filter(tenant=tenant).count()} campaigns")
        print(f"Created {Conversation.objects.filter(tenant=tenant).count()} conversations")
        
        return True
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        return False

def test_dashboard_endpoints(base_url, token):
    """Test all dashboard endpoints"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/api/messaging/dashboard/metrics/',
        '/api/messaging/dashboard/overview/',
        '/api/messaging/dashboard/comprehensive/',
        '/api/messaging/activity/recent/',
        '/api/messaging/campaigns/summary/',
    ]
    
    print(f"\nTesting dashboard endpoints...")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success!")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Pretty print the response for dashboard metrics
                if 'metrics' in endpoint:
                    print(f"Metrics data:")
                    if 'data' in data:
                        for key, value in data['data'].items():
                            print(f"  {key}: {value}")
                
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("\n" + "=" * 60)

def main():
    """Main test function"""
    print("Starting Dashboard Endpoints Test")
    print("=" * 60)
    
    # Get admin user and token
    token, user, tenant = get_admin_user_and_token()
    if not token:
        print("Failed to get admin user. Exiting.")
        return
    
    # Check if we need to create test data
    if tenant:
        print(f"Using existing data from tenant: {tenant.name}")
    else:
        print("No tenant found for admin user.")
        return
    
    # Test endpoints
    base_url = "http://127.0.0.1:8001"
    test_dashboard_endpoints(base_url, token)
    
    print("\nDashboard endpoints test completed!")

if __name__ == "__main__":
    main()
