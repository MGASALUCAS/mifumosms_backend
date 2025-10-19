#!/usr/bin/env python3
"""
Data seeding script for Mifumo SMS Backend Admin Dashboard
This script populates the admin dashboard with sample data for demonstration purposes.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from tenants.models import Tenant, Domain
from accounts.models import User
from messaging.models import Contact, Conversation, Message, Template, Campaign, Flow, Segment
from messaging.models_sms import (
    SMSProvider, SMSSenderID, SMSMessage, SMSTemplate, SMSDeliveryReport, 
    SMSBulkUpload, SMSSchedule, SenderNameRequest
)
from billing.models import (
    SMSPackage, BillingPlan, Subscription, Invoice, PaymentMethod, 
    SMSPurchase, SMSBalance, UsageRecord
)

User = get_user_model()

def create_sample_tenants():
    """Create sample tenants"""
    print("🏢 Creating sample tenants...")
    
    tenants_data = [
        {
            'name': 'Mifumo Labs',
            'subdomain': 'mifumo',
            'business_name': 'Mifumo Labs Ltd',
            'business_type': 'Technology',
            'phone_number': '+255700000000',
            'email': 'hello@mifumo.com',
            'address': 'Dar es Salaam, Tanzania',
            'wa_phone_number': '+255700000000',
            'wa_verified': True,
            'is_active': True,
            'trial_ends_at': timezone.now() + timedelta(days=30)
        },
        {
            'name': 'Tech Solutions Inc',
            'subdomain': 'techsolutions',
            'business_name': 'Tech Solutions Inc',
            'business_type': 'IT Services',
            'phone_number': '+255700000001',
            'email': 'info@techsolutions.co.tz',
            'address': 'Arusha, Tanzania',
            'wa_phone_number': '+255700000001',
            'wa_verified': True,
            'is_active': True,
            'trial_ends_at': timezone.now() + timedelta(days=15)
        },
        {
            'name': 'E-commerce Store',
            'subdomain': 'ecommerce',
            'business_name': 'E-commerce Store Ltd',
            'business_type': 'Retail',
            'phone_number': '+255700000002',
            'email': 'support@ecommerce.co.tz',
            'address': 'Mwanza, Tanzania',
            'wa_phone_number': '+255700000002',
            'wa_verified': False,
            'is_active': True,
            'trial_ends_at': timezone.now() + timedelta(days=7)
        }
    ]
    
    tenants = []
    for data in tenants_data:
        tenant, created = Tenant.objects.get_or_create(
            subdomain=data['subdomain'],
            defaults=data
        )
        tenants.append(tenant)
        if created:
            print(f"  ✅ Created tenant: {tenant.name}")
        else:
            print(f"  ℹ️  Tenant already exists: {tenant.name}")
    
    return tenants

def create_sample_domains(tenants):
    """Create sample domains for tenants"""
    print("🌐 Creating sample domains...")
    
    domain_data = [
        {'domain': 'mifumo.com', 'tenant': tenants[0]},
        {'domain': 'app.mifumo.com', 'tenant': tenants[0]},
        {'domain': 'techsolutions.co.tz', 'tenant': tenants[1]},
        {'domain': 'ecommerce.co.tz', 'tenant': tenants[2]},
    ]
    
    for data in domain_data:
        domain, created = Domain.objects.get_or_create(
            domain=data['domain'],
            defaults={'tenant': data['tenant']}
        )
        if created:
            print(f"  ✅ Created domain: {domain.domain}")

def create_sample_users(tenants):
    """Create sample users"""
    print("👥 Creating sample users...")
    
    users_data = [
        {
            'email': 'admin@mifumo.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        },
        {
            'email': 'john@mifumo.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': True,
            'is_superuser': False,
            'is_active': True
        },
        {
            'email': 'jane@techsolutions.co.tz',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'is_staff': False,
            'is_superuser': False,
            'is_active': True
        },
        {
            'email': 'bob@ecommerce.co.tz',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'is_staff': False,
            'is_superuser': False,
            'is_active': True
        }
    ]
    
    users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                **data,
                'username': data['email']
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✅ Created user: {user.email}")
        else:
            print(f"  ℹ️  User already exists: {user.email}")
        users.append(user)
    
    return users

def create_sample_contacts(users, tenants):
    """Create sample contacts"""
    print("📞 Creating sample contacts...")
    
    contacts_data = [
        {'name': 'Alice Johnson', 'phone_e164': '+255700000100', 'email': 'alice@example.com'},
        {'name': 'Bob Wilson', 'phone_e164': '+255700000101', 'email': 'bob@example.com'},
        {'name': 'Carol Brown', 'phone_e164': '+255700000102', 'email': 'carol@example.com'},
        {'name': 'David Lee', 'phone_e164': '+255700000103', 'email': 'david@example.com'},
        {'name': 'Eva Martinez', 'phone_e164': '+255700000104', 'email': 'eva@example.com'},
        {'name': 'Frank Taylor', 'phone_e164': '+255700000105', 'email': 'frank@example.com'},
        {'name': 'Grace Kim', 'phone_e164': '+255700000106', 'email': 'grace@example.com'},
        {'name': 'Henry Davis', 'phone_e164': '+255700000107', 'email': 'henry@example.com'},
    ]
    
    contacts = []
    for i, data in enumerate(contacts_data):
        contact, created = Contact.objects.get_or_create(
            phone_e164=data['phone_e164'],
            created_by=users[0],
            defaults={
                **data,
                'opt_in_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                'is_active': True,
                'tags': ['customer', 'vip'] if i < 3 else ['customer']
            }
        )
        if created:
            print(f"  ✅ Created contact: {contact.name}")
        contacts.append(contact)
    
    return contacts

def create_sample_sms_providers(tenants):
    """Create sample SMS providers"""
    print("📱 Creating sample SMS providers...")
    
    providers_data = [
        {
            'name': 'Beem Africa Primary',
            'provider_type': 'beem',
            'is_active': True,
            'is_default': True,
            'api_key': '62f8c3a2cb510335',
            'secret_key': 'YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ==',
            'api_url': 'https://apisms.beem.africa/v1',
            'cost_per_sms': Decimal('0.05'),
            'currency': 'USD'
        },
        {
            'name': 'Twilio Backup',
            'provider_type': 'twilio',
            'is_active': True,
            'is_default': False,
            'api_key': 'twilio_account_sid',
            'secret_key': 'twilio_auth_token',
            'api_url': 'https://api.twilio.com',
            'cost_per_sms': Decimal('0.08'),
            'currency': 'USD'
        }
    ]
    
    providers = []
    for tenant in tenants:
        for data in providers_data:
            provider, created = SMSProvider.objects.get_or_create(
                tenant=tenant,
                name=data['name'],
                defaults=data
            )
            if created:
                print(f"  ✅ Created SMS provider: {provider.name} for {tenant.name}")
            providers.append(provider)
    
    return providers

def create_sample_sms_packages():
    """Create sample SMS packages"""
    print("📦 Creating sample SMS packages...")
    
    packages_data = [
        {
            'name': 'Starter Pack',
            'package_type': 'lite',
            'credits': 100,
            'price': Decimal('5000.00'),
            'unit_price': Decimal('50.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['Basic SMS', 'Standard Support'],
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
            'features': ['Bulk SMS', 'Priority Support', 'Delivery Reports'],
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
            'features': ['Bulk SMS', 'Priority Support', 'Delivery Reports', 'Scheduling'],
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
            'features': ['Bulk SMS', '24/7 Support', 'Delivery Reports', 'Scheduling', 'API Access'],
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
            print(f"  ✅ Created SMS package: {package.name}")
        packages.append(package)
    
    return packages

def create_sample_sms_messages(tenants, contacts):
    """Create sample SMS messages"""
    print("💬 Creating sample SMS messages...")
    
    message_texts = [
        "Welcome to our service! Thank you for joining us.",
        "Your order has been confirmed. Order ID: #12345",
        "Reminder: Your appointment is tomorrow at 2 PM",
        "Your payment of TZS 50,000 has been received successfully",
        "New product alert: Check out our latest collection!",
        "Your account balance is TZS 25,000",
        "Thank you for your feedback. We appreciate it!",
        "System maintenance scheduled for tonight 11 PM - 1 AM"
    ]
    
    statuses = ['sent', 'delivered', 'failed', 'queued']
    
    for tenant in tenants:
        for i in range(20):  # Create 20 messages per tenant
            contact = random.choice(contacts)
            message = SMSMessage.objects.create(
                tenant=tenant,
                recipient_number=contact.phone_e164,
                text=random.choice(message_texts),
                status=random.choice(statuses),
                sent_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                cost_micro=random.randint(5000, 10000)  # 0.05 to 0.10 USD
            )
            if i == 0:  # Only print first message per tenant
                print(f"  ✅ Created SMS messages for {tenant.name}")

def create_sample_sender_requests(tenants):
    """Create sample sender name requests"""
    print("📝 Creating sample sender name requests...")
    
    sender_names = ['ALERT', 'NOTIFY', 'QUANTUM', 'INFO', 'SUPPORT', 'SERVICE']
    statuses = ['pending', 'approved', 'rejected']
    
    for tenant in tenants:
        for i in range(3):  # Create 3 requests per tenant
            request = SenderNameRequest.objects.create(
                tenant=tenant,
                sender_name=random.choice(sender_names),
                status=random.choice(statuses),
                requested_by=tenant.name,
                business_justification=f"Business need for {random.choice(sender_names)} sender ID",
                created_at=timezone.now() - timedelta(days=random.randint(1, 15))
            )
            if i == 0:  # Only print first request per tenant
                print(f"  ✅ Created sender requests for {tenant.name}")

def create_sample_billing_data(tenants, packages):
    """Create sample billing data"""
    print("💰 Creating sample billing data...")
    
    # Create billing plans
    plans_data = [
        {
            'name': 'Basic Plan',
            'description': 'Basic SMS service plan',
            'price': Decimal('10000.00'),
            'billing_cycle': 'monthly',
            'sms_limit': 1000,
            'is_active': True
        },
        {
            'name': 'Professional Plan',
            'description': 'Professional SMS service plan',
            'price': Decimal('25000.00'),
            'billing_cycle': 'monthly',
            'sms_limit': 5000,
            'is_active': True
        }
    ]
    
    plans = []
    for data in plans_data:
        plan, created = BillingPlan.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  ✅ Created billing plan: {plan.name}")
        plans.append(plan)
    
    # Create subscriptions
    for tenant in tenants:
        plan = random.choice(plans)
        subscription, created = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'status': 'active',
                'start_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                'end_date': timezone.now() + timedelta(days=random.randint(30, 365))
            }
        )
        if created:
            print(f"  ✅ Created subscription for {tenant.name}")

def create_sample_usage_records(tenants):
    """Create sample usage records"""
    print("📊 Creating sample usage records...")
    
    for tenant in tenants:
        for i in range(10):  # Create 10 usage records per tenant
            UsageRecord.objects.create(
                tenant=tenant,
                service_type='sms',
                usage_count=random.randint(1, 100),
                cost=Decimal(str(random.uniform(1.0, 50.0))),
                recorded_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
        print(f"  ✅ Created usage records for {tenant.name}")

@transaction.atomic
def seed_all_data():
    """Seed all sample data"""
    print("🌱 Starting data seeding for Mifumo SMS Backend Admin Dashboard...")
    print("=" * 60)
    
    try:
        # Create core data
        tenants = create_sample_tenants()
        create_sample_domains(tenants)
        users = create_sample_users(tenants)
        contacts = create_sample_contacts(users, tenants)
        
        # Create SMS data
        providers = create_sample_sms_providers(tenants)
        packages = create_sample_sms_packages()
        create_sample_sms_messages(tenants, contacts)
        create_sample_sender_requests(tenants)
        
        # Create billing data
        create_sample_billing_data(tenants, packages)
        create_sample_usage_records(tenants)
        
        print("=" * 60)
        print("🎉 Data seeding completed successfully!")
        print("\nAdmin Dashboard now contains:")
        print(f"  🏢 Tenants: {Tenant.objects.count()}")
        print(f"  👥 Users: {User.objects.count()}")
        print(f"  📞 Contacts: {Contact.objects.count()}")
        print(f"  📱 SMS Providers: {SMSProvider.objects.count()}")
        print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
        print(f"  💬 SMS Messages: {SMSMessage.objects.count()}")
        print(f"  📝 Sender Requests: {SenderNameRequest.objects.count()}")
        print(f"  💰 Billing Plans: {BillingPlan.objects.count()}")
        print(f"  📊 Usage Records: {UsageRecord.objects.count()}")
        print("\nYou can now access the admin dashboard with populated data!")
        
    except Exception as e:
        print(f"❌ Error during data seeding: {e}")
        raise

if __name__ == "__main__":
    seed_all_data()
