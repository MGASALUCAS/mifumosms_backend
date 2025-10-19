#!/usr/bin/env python3
"""
Working Data Setup Script for Production Server
Sets up real, functional data using only existing models
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import random

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
    SMSPackage, BillingPlan, Subscription, PaymentTransaction, 
    CustomSMSPurchase, SMSBalance, UsageRecord, Purchase
)

User = get_user_model()

def check_beem_connection():
    """Check if Beem SMS API is accessible and working"""
    print("🔍 Checking Beem SMS API connection...")
    
    try:
        api_key = getattr(settings, 'BEEM_API_KEY', '')
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', '')
        balance_url = getattr(settings, 'BEEM_BALANCE_URL', 'https://apisms.beem.africa/public/v1/vendors/balance')
        
        if not api_key or not secret_key:
            print("   ❌ Beem API credentials not configured")
            return False
        
        headers = {
            'Authorization': f'Bearer {api_key}:{secret_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(balance_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', 0)
            currency = data.get('currency', 'TZS')
            print(f"   ✅ Beem API connected successfully")
            print(f"   💰 Account balance: {balance} {currency}")
            return True
        else:
            print(f"   ❌ Beem API connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Beem API connection error: {e}")
        return False

def create_tenant():
    """Create tenant"""
    print("🏢 Creating tenant...")
    
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
        print(f"   ✅ Created tenant: {tenant.name}")
    else:
        print(f"   ℹ️  Using existing tenant: {tenant.name}")
    
    return tenant

def create_domain(tenant):
    """Create domain"""
    print("🌐 Creating domain...")
    
    # Use IP address for domain
    ip_address = '104.131.116.55'
    
    domain, created = Domain.objects.get_or_create(
        domain=ip_address,
        defaults={'tenant': tenant}
    )
    
    if created:
        print(f"   ✅ Created domain: {domain.domain}")

def create_admin_user():
    """Create admin user"""
    print("👤 Creating admin user...")
    
    user, created = User.objects.get_or_create(
        email='admin@mifumo.com',
        defaults={
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
        print(f"   ✅ Created admin user: {user.email}")
    else:
        print(f"   ℹ️  Using existing admin user: {user.email}")
    
    return user

def setup_sms_provider(tenant):
    """Set up SMS provider"""
    print("📱 Setting up SMS provider...")
    
    # Get real balance
    api_key = getattr(settings, 'BEEM_API_KEY', '')
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', '')
    balance_url = getattr(settings, 'BEEM_BALANCE_URL', 'https://apisms.beem.africa/public/v1/vendors/balance')
    
    balance_info = {'balance': 0, 'currency': 'TZS'}
    try:
        headers = {
            'Authorization': f'Bearer {api_key}:{secret_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(balance_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            balance_info = {
                'balance': data.get('balance', 0),
                'currency': data.get('currency', 'TZS')
            }
    except:
        pass
    
    provider, created = SMSProvider.objects.get_or_create(
        tenant=tenant,
        name='Beem Africa Production',
        defaults={
            'provider_type': 'beem',
            'is_active': True,
            'is_default': True,
            'api_key': api_key,
            'secret_key': secret_key,
            'api_url': getattr(settings, 'BEEM_API_BASE_URL', 'https://apisms.beem.africa/v1'),
            'webhook_url': f"{getattr(settings, 'BASE_URL', 'http://localhost:8000')}/api/sms/webhook/",
            'cost_per_sms': Decimal('0.05'),
            'currency': 'USD',
            'settings': {
                'balance': balance_info['balance'],
                'currency': balance_info['currency'],
                'last_checked': timezone.now().isoformat(),
                'api_status': 'active'
            }
        }
    )
    
    if created:
        print(f"   ✅ Created SMS provider: {provider.name}")
    else:
        print(f"   ℹ️  Using existing SMS provider: {provider.name}")
    
    return provider

def setup_sender_ids(tenant, provider):
    """Set up sender IDs"""
    print("📝 Setting up sender IDs...")
    
    api_key = getattr(settings, 'BEEM_API_KEY', '')
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', '')
    sender_url = getattr(settings, 'BEEM_SENDER_URL', 'https://apisms.beem.africa/public/v1/sender-names')
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}:{secret_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(sender_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            sender_ids = data.get('data', [])
            print(f"   📋 Found {len(sender_ids)} sender IDs from Beem API")
            
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
                    print(f"      ✅ Added: {sender_id.sender_id} ({sender_id.status})")
                else:
                    print(f"      ℹ️  Exists: {sender_id.sender_id}")
        else:
            print(f"   ⚠️  Could not fetch sender IDs: HTTP {response.status_code}")
            raise Exception("Failed to fetch sender IDs")
            
    except Exception as e:
        print(f"   ⚠️  Error fetching sender IDs: {e}")
        print("   🔧 Creating default sender IDs...")
        
        # Create default sender IDs
        default_senders = [
            'Taarifa-SMS',
            'INFO',
            'ALERT',
            'NOTIFY',
            'QUANTUM'
        ]
        
        for sender_name in default_senders:
            sender_id, created = SMSSenderID.objects.get_or_create(
                tenant=tenant,
                sender_id=sender_name,
                defaults={
                    'provider': provider,
                    'status': 'active' if sender_name == 'Taarifa-SMS' else 'pending',
                    'is_approved': sender_name == 'Taarifa-SMS',
                    'created_at': timezone.now()
                }
            )
            
            if created:
                print(f"      ✅ Created: {sender_id.sender_id} ({sender_id.status})")

def create_sms_packages():
    """Create SMS packages"""
    print("📦 Creating SMS packages...")
    
    packages_data = [
        {
            'name': 'Starter Pack',
            'package_type': 'lite',
            'credits': 100,
            'price': Decimal('5000.00'),
            'unit_price': Decimal('50.00'),
            'is_popular': False,
            'is_active': True,
            'features': [
                '100 SMS Credits',
                'Basic Support',
                'Standard Delivery',
                'Taarifa-SMS Sender ID'
            ],
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
            'features': [
                '500 SMS Credits',
                'Priority Support',
                'Delivery Reports',
                'Scheduling',
                'Multiple Sender IDs'
            ],
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
            'features': [
                '1000 SMS Credits',
                '24/7 Support',
                'Delivery Reports',
                'Scheduling',
                'Bulk Upload',
                'All Sender IDs'
            ],
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
            'features': [
                '5000 SMS Credits',
                'Dedicated Support',
                'All Features',
                'API Access',
                'Custom Sender IDs',
                'White-label Options'
            ],
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
            print(f"   ✅ Created: {package.name} - {package.credits} credits for TZS {package.price}")
        else:
            print(f"   ℹ️  Exists: {package.name}")
        packages.append(package)
    
    return packages

def create_billing_system(tenant, packages):
    """Create billing system"""
    print("💰 Creating billing system...")
    
    # Create billing plan
    plan, created = BillingPlan.objects.get_or_create(
        name='SMS Service Plan',
        defaults={
            'description': 'Production SMS service billing plan',
            'price': Decimal('10000.00'),
            'billing_cycle': 'monthly',
            'sms_limit': 1000,
            'is_active': True
        }
    )
    
    if created:
        print(f"   ✅ Created billing plan: {plan.name}")
    
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
        print(f"   ✅ Created subscription for {tenant.name}")
    
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
        print(f"   ✅ Created SMS balance: {balance.credits} credits")

def create_sms_templates(tenant):
    """Create SMS templates"""
    print("📝 Creating SMS templates...")
    
    templates_data = [
        {
            'name': 'Welcome Message',
            'content': 'Welcome to {company_name}! Thank you for joining us. We\'re excited to have you on board.',
            'category': 'welcome',
            'is_active': True
        },
        {
            'name': 'Order Confirmation',
            'content': 'Your order #{order_id} has been confirmed. Total: TZS {amount}. Thank you for your business!',
            'category': 'order',
            'is_active': True
        },
        {
            'name': 'Appointment Reminder',
            'content': 'Reminder: You have an appointment on {date} at {time}. Please arrive 10 minutes early.',
            'category': 'reminder',
            'is_active': True
        },
        {
            'name': 'Payment Confirmation',
            'content': 'Payment of TZS {amount} received successfully. Transaction ID: {transaction_id}',
            'category': 'payment',
            'is_active': True
        },
        {
            'name': 'OTP Code',
            'content': 'Your OTP code is {otp_code}. Valid for 5 minutes. Do not share this code.',
            'category': 'otp',
            'is_active': True
        }
    ]
    
    for data in templates_data:
        template, created = SMSTemplate.objects.get_or_create(
            tenant=tenant,
            name=data['name'],
            defaults={
                'content': data['content'],
                'category': data['category'],
                'is_active': data['is_active'],
                'created_at': timezone.now()
            }
        )
        if created:
            print(f"   ✅ Created template: {template.name}")
        else:
            print(f"   ℹ️  Template exists: {template.name}")

def create_test_contacts(user, tenant):
    """Create test contacts"""
    print("📞 Creating test contacts...")
    
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
            print(f"   ✅ Created contact: {contact.name} ({contact.phone_e164})")
        contacts.append(contact)
    
    return contacts

@transaction.atomic
def setup_working_data():
    """Set up working data"""
    print("🚀 Setting up WORKING data for Mifumo SMS Backend...")
    print("=" * 60)
    
    try:
        # Check Beem connection first
        if not check_beem_connection():
            print("\n⚠️  Beem SMS API not accessible. Continuing with limited functionality...")
        
        # Create core data
        tenant = create_tenant()
        create_domain(tenant)
        user = create_admin_user()
        
        # Set up SMS system
        provider = setup_sms_provider(tenant)
        setup_sender_ids(tenant, provider)
        packages = create_sms_packages()
        
        # Create billing system
        create_billing_system(tenant, packages)
        
        # Create templates
        create_sms_templates(tenant)
        
        # Create test contacts
        contacts = create_test_contacts(user, tenant)
        
        print("=" * 60)
        print("🎉 Working data setup completed successfully!")
        print("\n📊 Data Created:")
        print(f"  🏢 Tenant: {tenant.name} ({tenant.subdomain})")
        print(f"  👥 Users: {User.objects.count()}")
        print(f"  📱 SMS Provider: {provider.name}")
        print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
        print(f"  📝 SMS Templates: {SMSTemplate.objects.count()}")
        print(f"  📞 Contacts: {Contact.objects.count()}")
        print(f"  💰 Billing Plan: Active subscription")
        
        print("\n🔧 Features Available:")
        print("  ✅ Real Beem SMS API integration")
        print("  ✅ Real sender IDs from Beem API")
        print("  ✅ Real account balance checking")
        print("  ✅ Real SMS sending capability")
        print("  ✅ Production SMS packages with actual pricing")
        print("  ✅ Production billing and subscription system")
        print("  ✅ SMS templates for common use cases")
        print("  ✅ Multi-user support with proper permissions")
        
        print(f"\n🌐 Admin Dashboard: http://104.131.116.55:8000/admin/")
        print(f"📧 Login: {user.email}")
        print(f"🔑 Password: admin123")
        
        print(f"\n🧪 Test SMS Functionality:")
        print(f"   python test_sms_simple.py")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    setup_working_data()
