#!/usr/bin/env python3
"""
Minimal Setup Script - Creates basic working data
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from tenants.models import Tenant, Domain
from accounts.models import User
from messaging.models_sms import SMSProvider, SMSSenderID, SMSTemplate
from billing.models import SMSPackage, BillingPlan, Subscription, SMSBalance

User = get_user_model()

def create_minimal_data():
    """Create minimal working data"""
    print("🚀 Creating minimal working data...")
    print("=" * 50)
    
    try:
        # 1. Create tenant
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
                'is_active': True
            }
        )
        print(f"   ✅ Tenant: {tenant.name}")
        
        # 2. Create domain
        print("🌐 Creating domain...")
        domain, created = Domain.objects.get_or_create(
            domain='104.131.116.55',
            defaults={'tenant': tenant}
        )
        print(f"   ✅ Domain: {domain.domain}")
        
        # 3. Create admin user
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
        print(f"   ✅ Admin: {user.email}")
        
        # 4. Create SMS provider
        print("📱 Creating SMS provider...")
        provider, created = SMSProvider.objects.get_or_create(
            tenant=tenant,
            name='Beem Africa',
            defaults={
                'provider_type': 'beem',
                'is_active': True,
                'is_default': True,
                'api_key': '62f8c3a2cb510335',
                'secret_key': 'YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ==',
                'api_url': 'https://apisms.beem.africa/v1',
                'cost_per_sms': Decimal('0.05'),
                'currency': 'USD'
            }
        )
        print(f"   ✅ Provider: {provider.name}")
        
        # 5. Create sender IDs
        print("📝 Creating sender IDs...")
        sender_names = ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY']
        for sender_name in sender_names:
            sender_id, created = SMSSenderID.objects.get_or_create(
                tenant=tenant,
                sender_id=sender_name,
                defaults={
                    'provider': provider,
                    'status': 'active' if sender_name == 'Taarifa-SMS' else 'pending',
                    'sample_content': f'Sample message for {sender_name}'
                }
            )
            if created:
                print(f"   ✅ Sender ID: {sender_id.sender_id}")
        
        # 6. Create SMS packages
        print("📦 Creating SMS packages...")
        packages_data = [
            {
                'name': 'Starter Pack',
                'package_type': 'lite',
                'credits': 100,
                'price': Decimal('5000.00'),
                'unit_price': Decimal('50.00'),
                'is_active': True,
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
                'default_sender_id': 'Taarifa-SMS',
                'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY'],
                'sender_id_restriction': 'allowed_list'
            }
        ]
        
        for data in packages_data:
            package, created = SMSPackage.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                print(f"   ✅ Package: {package.name}")
        
        # 7. Create billing plan
        print("💰 Creating billing plan...")
        plan, created = BillingPlan.objects.get_or_create(
            name='SMS Service Plan',
            defaults={
                'plan_type': 'basic',
                'description': 'SMS service billing plan',
                'price': Decimal('10000.00'),
                'currency': 'TZS',
                'billing_cycle': 'monthly',
                'max_contacts': 1000,
                'max_campaigns': 10,
                'max_sms_per_month': 1000,
                'features': ['SMS sending', 'Basic support'],
                'is_active': True
            }
        )
        print(f"   ✅ Plan: {plan.name}")
        
        # 8. Create subscription
        print("📋 Creating subscription...")
        subscription, created = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
                'cancel_at_period_end': False
            }
        )
        print(f"   ✅ Subscription: {subscription.status}")
        
        # 9. Create SMS balance
        print("💳 Creating SMS balance...")
        balance, created = SMSBalance.objects.get_or_create(
            tenant=tenant,
            defaults={
                'credits': 1000,
                'used_credits': 0,
                'last_updated': timezone.now()
            }
        )
        print(f"   ✅ Balance: {balance.credits} credits")
        
        # 10. Create SMS templates
        print("📝 Creating SMS templates...")
        templates_data = [
            {
                'name': 'Welcome Message',
                'content': 'Welcome to {company_name}! Thank you for joining us.',
                'category': 'welcome',
                'is_active': True
            },
            {
                'name': 'Order Confirmation',
                'content': 'Your order #{order_id} has been confirmed. Total: TZS {amount}.',
                'category': 'order',
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
                    'is_active': data['is_active']
                }
            )
            if created:
                print(f"   ✅ Template: {template.name}")
        
        print("=" * 50)
        print("🎉 Minimal setup completed successfully!")
        print("\n📊 Data Created:")
        print(f"  🏢 Tenant: {tenant.name}")
        print(f"  👤 Admin: {user.email}")
        print(f"  📱 SMS Provider: {provider.name}")
        print(f"  📝 Sender IDs: {SMSSenderID.objects.filter(tenant=tenant).count()}")
        print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
        print(f"  📋 Billing Plan: {plan.name}")
        print(f"  💰 SMS Balance: {balance.credits} credits")
        print(f"  📝 Templates: {SMSTemplate.objects.filter(tenant=tenant).count()}")
        
        print(f"\n🌐 Admin Dashboard: http://104.131.116.55:8000/admin/")
        print(f"📧 Login: {user.email}")
        print(f"🔑 Password: admin123")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_minimal_data()
