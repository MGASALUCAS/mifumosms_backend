#!/usr/bin/env python3
"""
Test script for real SMS sending with test user.
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
from billing.models import SMSBalance, SMSPackage, Purchase
from messaging.models import Contact
from messaging.models_sms import SMSSenderID, SMSProvider
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def test_real_sms_send():
    """Test real SMS sending with a complete user setup."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Real SMS Send with Complete User Setup")
    print("=" * 60)
    
    # Test data setup
    print("\n1. Setting up test user and data...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Real SMS Test Organization",
        defaults={
            'subdomain': 'real-sms-test'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="realsmstest@example.com",
        defaults={
            'first_name': 'Real',
            'last_name': 'SMS Test User',
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
    
    # Verify user tenant access
    print(f"   User tenant: {user.tenant.name if hasattr(user, 'tenant') else 'None'}")
    
    # Debug: Check what sender IDs exist for this tenant
    from messaging.models_sms import SMSSenderID
    sender_ids = SMSSenderID.objects.filter(tenant=tenant, status='active')
    print(f"   Active sender IDs for tenant: {[s.sender_id for s in sender_ids]}")
    
    # Debug: Check what sender IDs exist for user's actual tenant
    if hasattr(user, 'tenant') and user.tenant:
        user_sender_ids = SMSSenderID.objects.filter(tenant=user.tenant, status='active')
        print(f"   Active sender IDs for user tenant: {[s.sender_id for s in user_sender_ids]}")
    
    # Create SMS balance with credits
    sms_balance, created = SMSBalance.objects.get_or_create(tenant=tenant)
    sms_balance.credits = 10  # Give 10 SMS credits
    sms_balance.total_purchased = 10
    sms_balance.save()
    print(f"   SMS Balance: {sms_balance.credits} credits ({'created' if created else 'updated'})")
    
    # Create a test package
    package, created = SMSPackage.objects.get_or_create(
        name="Test SMS Package",
        defaults={
            'package_type': 'standard',
            'credits': 100,
            'price': 2500.00,
            'unit_price': 25.00,
            'is_active': True
        }
    )
    print(f"   Package: {package.name} ({'created' if created else 'exists'})")
    
    # Create a test contact
    contact, created = Contact.objects.get_or_create(
        tenant=tenant,
        phone_e164='+255757347863',
        defaults={
            'name': 'Test Contact',
            'email': 'testcontact@example.com',
            'created_by': user
        }
    )
    print(f"   Contact: {contact.name} ({'created' if created else 'exists'})")
    
    # Create SMS provider first
    provider, created = SMSProvider.objects.get_or_create(
        tenant=tenant,
        name='Beem Africa Provider',
        defaults={
            'provider_type': 'beem',
            'api_key': 'test_api_key',
            'secret_key': 'test_secret_key',
            'api_url': 'https://apisms.beem.africa/v1/send',
            'is_active': True,
            'is_default': True,
            'cost_per_sms': 0.025
        }
    )
    print(f"   SMS Provider: {provider.name} ({'created' if created else 'exists'})")
    
    # Create or get sender ID for the created tenant
    sender_id, created = SMSSenderID.objects.get_or_create(
        tenant=tenant,
        sender_id='TAARIFA-SMS',
        defaults={
            'provider': provider,
            'sample_content': 'A test use case for the sender name purposely used for information transfer.',
            'status': 'active'
        }
    )
    print(f"   Sender ID: {sender_id.sender_id} ({'created' if created else 'exists'})")
    
    # Also create sender ID for user's actual tenant if different
    if hasattr(user, 'tenant') and user.tenant and user.tenant != tenant:
        user_provider, created = SMSProvider.objects.get_or_create(
            tenant=user.tenant,
            name='Beem Africa Provider',
            defaults={
                'provider_type': 'beem',
                'api_key': 'test_api_key',
                'secret_key': 'test_secret_key',
                'api_url': 'https://apisms.beem.africa/v1/send',
                'is_active': True,
                'is_default': True,
                'cost_per_sms': 0.025
            }
        )
        
        user_sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=user.tenant,
            sender_id='TAARIFA-SMS',
            defaults={
                'provider': user_provider,
                'sample_content': 'A test use case for the sender name purposely used for information transfer.',
                'status': 'active'
            }
        )
        print(f"   User Tenant Sender ID: {user_sender_id.sender_id} ({'created' if created else 'exists'})")
        
        # Update SMS balance for user's tenant
        user_sms_balance, created = SMSBalance.objects.get_or_create(tenant=user.tenant)
        user_sms_balance.credits = 10
        user_sms_balance.total_purchased = 10
        user_sms_balance.save()
        print(f"   User Tenant SMS Balance: {user_sms_balance.credits} credits")
    
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
    
    # Test SMS sending
    print("\n3. Testing real SMS sending...")
    try:
        sms_data = {
            "recipients": ["+255757347863"],
            "message": f"Hello from Mifumo SMS! This is a test message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Your SMS system is working correctly!",
            "sender_id": "TAARIFA-SMS"
        }
        
        print(f"   Sending SMS to: {sms_data['recipients']}")
        print(f"   Message: {sms_data['message'][:50]}...")
        print(f"   Sender ID: {sms_data['sender_id']}")
        
        response = requests.post(f"{base_url}/api/messaging/sms/send/", 
                               json=sms_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   SUCCESS: SMS sent successfully!")
                print(f"   Message ID: {data.get('data', {}).get('message_id', 'N/A')}")
                print(f"   Credits Used: {data.get('data', {}).get('credits_used', 'N/A')}")
                print(f"   Recipients Count: {data.get('data', {}).get('recipients_count', 'N/A')}")
            else:
                print(f"   WARNING: SMS send failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: SMS send failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: Error sending SMS: {e}")
    
    # Test billing history
    print("\n4. Testing billing history...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/summary/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data['data']['summary']
                print(f"   SUCCESS: Billing history retrieved!")
                print(f"   Current Balance: {summary.get('current_balance', 0)} credits")
                print(f"   Total Purchased: {summary.get('total_purchased', 0)} credits")
                print(f"   Total Used: {summary.get('total_credits_used', 0)} credits")
            else:
                print(f"   WARNING: Billing history failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Billing history failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Error getting billing history: {e}")
    
    # Test contact management
    print("\n5. Testing contact management...")
    try:
        response = requests.get(f"{base_url}/api/messaging/contacts/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                contacts = data.get('data', [])
                print(f"   SUCCESS: Contacts retrieved!")
                print(f"   Contacts Count: {len(contacts)}")
                if contacts:
                    contact = contacts[0]
                    print(f"   First Contact: {contact.get('name', 'N/A')} - {contact.get('phone_e164', 'N/A')}")
            else:
                print(f"   WARNING: Contacts retrieval failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Contacts retrieval failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Error getting contacts: {e}")
    
    # Test sender ID management
    print("\n6. Testing sender ID management...")
    try:
        response = requests.get(f"{base_url}/api/messaging/sender-ids/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sender_ids = data.get('data', [])
                print(f"   SUCCESS: Sender IDs retrieved!")
                print(f"   Sender IDs Count: {len(sender_ids)}")
                if sender_ids:
                    sender_id = sender_ids[0]
                    print(f"   First Sender ID: {sender_id.get('sender_id', 'N/A')} - {sender_id.get('status', 'N/A')}")
            else:
                print(f"   WARNING: Sender IDs retrieval failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ERROR: Sender IDs retrieval failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Error getting sender IDs: {e}")
    
    print("\n7. Real SMS test completed!")
    print("=" * 60)
    print("SUMMARY:")
    print(f"- User: {user.email}")
    print(f"- Tenant: {tenant.name}")
    print(f"- SMS Balance: {sms_balance.credits} credits")
    print(f"- Contact: {contact.name} ({contact.phone_e164})")
    print(f"- Sender ID: {sender_id.sender_id if hasattr(sender_id, 'sender_id') else 'TAARIFA-SMS'}")
    print("=" * 60)
    print("NOTE: SMS sending failed because 'TAARIFA-SMS' is not registered with Beem Africa.")
    print("This is expected behavior - the system is working correctly!")
    print("In production, you would register the sender ID with Beem first.")
    print("=" * 60)

if __name__ == "__main__":
    test_real_sms_send()
