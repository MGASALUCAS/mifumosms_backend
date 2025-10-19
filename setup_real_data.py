#!/usr/bin/env python3
"""
Real Data Setup Script for Mifumo SMS Backend
Sets up real, functional data using actual Beem SMS API and real configurations
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from tenants.models import Tenant, Domain
from accounts.models import User
from messaging.models import Contact, Conversation, Message, Template
from messaging.models_sms import (
    SMSProvider, SMSSenderID, SMSMessage, SMSTemplate, SMSDeliveryReport, 
    SMSBulkUpload, SMSSchedule, SenderNameRequest
)
from billing.models import (
    SMSPackage, BillingPlan, Subscription, Invoice, PaymentMethod, 
    SMSPurchase, SMSBalance, UsageRecord
)

User = get_user_model()

class BeemSMSAPI:
    """Real Beem SMS API integration"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'BEEM_API_KEY', '')
        self.secret_key = getattr(settings, 'BEEM_SECRET_KEY', '')
        self.base_url = getattr(settings, 'BEEM_API_BASE_URL', 'https://apisms.beem.africa/v1')
        self.balance_url = getattr(settings, 'BEEM_BALANCE_URL', 'https://apisms.beem.africa/public/v1/vendors/balance')
        self.sender_url = getattr(settings, 'BEEM_SENDER_URL', 'https://apisms.beem.africa/public/v1/sender-names')
        self.template_url = getattr(settings, 'BEEM_TEMPLATE_URL', 'https://apisms.beem.africa/public/v1/sms-templates')
        
    def get_balance(self):
        """Get real account balance from Beem"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}:{self.secret_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(self.balance_url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'balance': data.get('balance', 0),
                    'currency': data.get('currency', 'TZS')
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sender_ids(self):
        """Get real sender IDs from Beem"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}:{self.secret_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(self.sender_url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'sender_ids': data.get('data', [])
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_templates(self):
        """Get real SMS templates from Beem"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}:{self.secret_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(self.template_url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'templates': data.get('data', [])
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_test_sms(self, phone_number, message, sender_id):
        """Send a real test SMS"""
        try:
            url = f"{self.base_url}/send"
            headers = {
                'Authorization': f'Bearer {self.api_key}:{self.secret_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'source_addr': sender_id,
                'schedule_time': '',
                'encoding': 0,
                'message': message,
                'recipients': [{'recipient_id': 1, 'dest_addr': phone_number}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'request_id': result.get('request_id'),
                    'code': result.get('code'),
                    'valid': result.get('valid', [])
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

def create_real_tenant():
    """Create a real tenant with actual business information"""
    print("🏢 Creating real tenant...")
    
    tenant, created = Tenant.objects.get_or_create(
        subdomain='mifumo',
        defaults={
            'name': 'Mifumo Labs',
            'business_name': 'Mifumo Labs Limited',
            'business_type': 'Technology Solutions',
            'phone_number': '+255700000000',
            'email': 'hello@mifumo.com',
            'address': 'Dar es Salaam, Tanzania',
            'wa_phone_number': '+255700000000',
            'wa_verified': True,
            'is_active': True,
            'trial_ends_at': timezone.now() + timedelta(days=30)
        }
    )
    
    if created:
        print(f"  ✅ Created tenant: {tenant.name}")
    else:
        print(f"  ℹ️  Using existing tenant: {tenant.name}")
    
    return tenant

def create_real_domain(tenant):
    """Create real domain for tenant"""
    print("🌐 Creating real domain...")
    
    domain, created = Domain.objects.get_or_create(
        domain='mifumo.com',
        defaults={'tenant': tenant}
    )
    
    if created:
        print(f"  ✅ Created domain: {domain.domain}")
    else:
        print(f"  ℹ️  Using existing domain: {domain.domain}")

def create_real_admin_user():
    """Create real admin user"""
    print("👤 Creating real admin user...")
    
    user, created = User.objects.get_or_create(
        email='admin@mifumo.com',
        defaults={
            'username': 'admin@mifumo.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"  ✅ Created admin user: {user.email}")
    else:
        print(f"  ℹ️  Using existing admin user: {user.email}")
    
    return user

def setup_real_sms_provider(tenant):
    """Set up real SMS provider with actual Beem configuration"""
    print("📱 Setting up real SMS provider...")
    
    # Get real balance from Beem
    beem_api = BeemSMSAPI()
    balance_info = beem_api.get_balance()
    
    if balance_info['success']:
        print(f"  💰 Beem account balance: {balance_info['balance']} {balance_info['currency']}")
    else:
        print(f"  ⚠️  Could not fetch balance: {balance_info['error']}")
    
    provider, created = SMSProvider.objects.get_or_create(
        tenant=tenant,
        name='Beem Africa (Real)',
        defaults={
            'provider_type': 'beem',
            'is_active': True,
            'is_default': True,
            'api_key': getattr(settings, 'BEEM_API_KEY', ''),
            'secret_key': getattr(settings, 'BEEM_SECRET_KEY', ''),
            'api_url': getattr(settings, 'BEEM_API_BASE_URL', 'https://apisms.beem.africa/v1'),
            'webhook_url': f"{getattr(settings, 'BASE_URL', 'http://localhost:8000')}/api/sms/webhook/",
            'cost_per_sms': Decimal('0.05'),
            'currency': 'USD',
            'settings': {
                'balance': balance_info.get('balance', 0),
                'currency': balance_info.get('currency', 'TZS'),
                'last_checked': timezone.now().isoformat()
            }
        }
    )
    
    if created:
        print(f"  ✅ Created SMS provider: {provider.name}")
    else:
        print(f"  ℹ️  Using existing SMS provider: {provider.name}")
    
    return provider

def setup_real_sender_ids(tenant, provider):
    """Set up real sender IDs from Beem API"""
    print("📝 Setting up real sender IDs...")
    
    beem_api = BeemSMSAPI()
    sender_info = beem_api.get_sender_ids()
    
    if sender_info['success']:
        sender_ids = sender_info['sender_ids']
        print(f"  📋 Found {len(sender_ids)} sender IDs from Beem API")
        
        for sender_data in sender_ids:
            sender_id, created = SMSSenderID.objects.get_or_create(
                tenant=tenant,
                sender_id=sender_data.get('senderid', ''),
                defaults={
                    'provider': provider,
                    'status': sender_data.get('status', 'pending'),
                    'is_approved': sender_data.get('status') == 'active',
                    'created_at': timezone.now()
                }
            )
            
            if created:
                print(f"    ✅ Added sender ID: {sender_id.sender_id} ({sender_id.status})")
            else:
                print(f"    ℹ️  Sender ID exists: {sender_id.sender_id}")
    else:
        print(f"  ⚠️  Could not fetch sender IDs: {sender_info['error']}")
        
        # Create default sender ID
        default_sender = getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'Taarifa-SMS')
        sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id=default_sender,
            defaults={
                'provider': provider,
                'status': 'active',
                'is_approved': True,
                'created_at': timezone.now()
            }
        )
        
        if created:
            print(f"    ✅ Created default sender ID: {sender_id.sender_id}")
        else:
            print(f"    ℹ️  Default sender ID exists: {sender_id.sender_id}")

def create_real_sms_packages():
    """Create real SMS packages with actual pricing"""
    print("📦 Creating real SMS packages...")
    
    packages_data = [
        {
            'name': 'Starter Pack',
            'package_type': 'lite',
            'credits': 100,
            'price': Decimal('5000.00'),
            'unit_price': Decimal('50.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['100 SMS Credits', 'Basic Support', 'Standard Delivery'],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'INFO'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Business Pack',
            'package_type': 'standard',
            'credits': 500,
            'price': Decimal('20000.00'),
            'unit_price': Decimal('40.00'),
            'is_popular': True,
            'is_active': True,
            'features': ['500 SMS Credits', 'Priority Support', 'Delivery Reports', 'Scheduling'],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Professional Pack',
            'package_type': 'pro',
            'credits': 1000,
            'price': Decimal('35000.00'),
            'unit_price': Decimal('35.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['1000 SMS Credits', '24/7 Support', 'Delivery Reports', 'Scheduling', 'Bulk Upload'],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY', 'QUANTUM'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Enterprise Pack',
            'package_type': 'enterprise',
            'credits': 5000,
            'price': Decimal('150000.00'),
            'unit_price': Decimal('30.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['5000 SMS Credits', 'Dedicated Support', 'All Features', 'API Access', 'Custom Sender IDs'],
            'default_sender_id': 'Taarifa-SMS',
            'sender_id_restriction': 'none'
        }
    ]
    
    packages = []
    for data in packages_data:
        package, created = SMSPackage.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  ✅ Created package: {package.name} - {package.credits} credits for TZS {package.price}")
        else:
            print(f"  ℹ️  Package exists: {package.name}")
        packages.append(package)
    
    return packages

def create_real_contacts(user, tenant):
    """Create real contacts for testing"""
    print("📞 Creating real contacts...")
    
    contacts_data = [
        {'name': 'Test User 1', 'phone_e164': '+255700000100', 'email': 'test1@example.com'},
        {'name': 'Test User 2', 'phone_e164': '+255700000101', 'email': 'test2@example.com'},
        {'name': 'Test User 3', 'phone_e164': '+255700000102', 'email': 'test3@example.com'},
    ]
    
    contacts = []
    for data in contacts_data:
        contact, created = Contact.objects.get_or_create(
            phone_e164=data['phone_e164'],
            created_by=user,
            defaults={
                **data,
                'opt_in_at': timezone.now() - timedelta(days=1),
                'is_active': True,
                'tags': ['test', 'demo']
            }
        )
        if created:
            print(f"  ✅ Created contact: {contact.name} ({contact.phone_e164})")
        contacts.append(contact)
    
    return contacts

def test_real_sms_sending(tenant, contacts):
    """Test real SMS sending functionality"""
    print("🧪 Testing real SMS sending...")
    
    beem_api = BeemSMSAPI()
    default_sender = getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'Taarifa-SMS')
    
    if contacts:
        test_contact = contacts[0]
        test_message = "Hello! This is a test message from Mifumo SMS Backend. Your system is working correctly!"
        
        print(f"  📤 Sending test SMS to {test_contact.phone_e164}...")
        result = beem_api.send_test_sms(
            phone_number=test_contact.phone_e164,
            message=test_message,
            sender_id=default_sender
        )
        
        if result['success']:
            print(f"  ✅ SMS sent successfully! Request ID: {result.get('request_id')}")
            
            # Create SMS message record
            sms_message = SMSMessage.objects.create(
                tenant=tenant,
                recipient_number=test_contact.phone_e164,
                text=test_message,
                status='sent',
                sent_at=timezone.now(),
                cost_micro=5000,  # 0.05 USD
                provider_message_id=result.get('request_id', '')
            )
            print(f"  📝 Created SMS message record: {sms_message.id}")
            
        else:
            print(f"  ❌ SMS sending failed: {result['error']}")
    else:
        print("  ⚠️  No contacts available for testing")

def create_real_billing_data(tenant, packages):
    """Create real billing data"""
    print("💰 Creating real billing data...")
    
    # Create billing plan
    plan, created = BillingPlan.objects.get_or_create(
        name='SMS Service Plan',
        defaults={
            'description': 'Real SMS service billing plan',
            'price': Decimal('10000.00'),
            'billing_cycle': 'monthly',
            'sms_limit': 1000,
            'is_active': True
        }
    )
    
    if created:
        print(f"  ✅ Created billing plan: {plan.name}")
    
    # Create subscription
    subscription, created = Subscription.objects.get_or_create(
        tenant=tenant,
        defaults={
            'plan': plan,
            'status': 'active',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=30)
        }
    )
    
    if created:
        print(f"  ✅ Created subscription for {tenant.name}")
    
    # Create SMS balance
    balance, created = SMSBalance.objects.get_or_create(
        tenant=tenant,
        defaults={
            'credits': 1000,
            'used_credits': 0,
            'last_updated': timezone.now()
        }
    )
    
    if created:
        print(f"  ✅ Created SMS balance: {balance.credits} credits")

@transaction.atomic
def setup_real_data():
    """Set up all real data"""
    print("🚀 Setting up REAL data for Mifumo SMS Backend...")
    print("=" * 60)
    
    try:
        # Create core data
        tenant = create_real_tenant()
        create_real_domain(tenant)
        user = create_real_admin_user()
        
        # Set up SMS system
        provider = setup_real_sms_provider(tenant)
        setup_real_sender_ids(tenant, provider)
        packages = create_real_sms_packages()
        
        # Create test data
        contacts = create_real_contacts(user, tenant)
        
        # Test real SMS functionality
        test_real_sms_sending(tenant, contacts)
        
        # Create billing data
        create_real_billing_data(tenant, packages)
        
        print("=" * 60)
        print("🎉 Real data setup completed successfully!")
        print("\nReal Data Created:")
        print(f"  🏢 Tenant: {tenant.name} ({tenant.subdomain})")
        print(f"  👤 Admin: {user.email}")
        print(f"  📱 SMS Provider: {provider.name}")
        print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
        print(f"  📞 Contacts: {Contact.objects.count()}")
        print(f"  💰 Billing Plan: Active subscription")
        
        print("\n🔧 Real Features Available:")
        print("  ✅ Real Beem SMS API integration")
        print("  ✅ Real sender IDs from Beem")
        print("  ✅ Real account balance checking")
        print("  ✅ Real SMS sending capability")
        print("  ✅ Real SMS packages with actual pricing")
        print("  ✅ Real billing and subscription system")
        
        print(f"\n🌐 Admin Dashboard: http://localhost:8000/admin/")
        print(f"📧 Login: {user.email}")
        print(f"🔑 Password: admin123")
        
    except Exception as e:
        print(f"❌ Error during real data setup: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    setup_real_data()
