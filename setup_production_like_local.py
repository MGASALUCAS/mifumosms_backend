#!/usr/bin/env python3
"""
Production Setup Script - Matches Local Behavior
Creates admin user with tenant, SMS provider, and sender IDs like in local development
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
from tenants.models import Tenant, Domain, Membership
from accounts.models import User
from messaging.models_sms import SMSProvider, SMSSenderID
from billing.models import SMSPackage, BillingPlan, Subscription, SMSBalance

User = get_user_model()

def create_admin_like_local():
    """Create admin user exactly like local development"""
    print("🚀 Creating admin user like local development...")
    print("=" * 60)
    
    try:
        # 1. Create admin user (like local)
        print("👤 Creating admin user...")
        user, created = User.objects.get_or_create(
            email='admin@mifumo.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            print(f"   ✅ Created admin user: {user.email}")
        else:
            print(f"   ℹ️  Admin user already exists: {user.email}")
            user.set_password('admin123')
            user.save()
            print(f"   🔑 Updated password for: {user.email}")
        
        # 2. Create tenant (like local)
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
        
        if created:
            print(f"   ✅ Created tenant: {tenant.name}")
        else:
            print(f"   ℹ️  Tenant already exists: {tenant.name}")
        
        # 3. Create domain
        print("🌐 Creating domain...")
        domain, created = Domain.objects.get_or_create(
            domain='104.131.116.55',
            defaults={'tenant': tenant}
        )
        if created:
            print(f"   ✅ Created domain: {domain.domain}")
        
        # 4. Create membership (like local)
        print("👥 Creating membership...")
        membership, created = Membership.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={
                'role': 'owner',
                'status': 'active'
            }
        )
        if created:
            print(f"   ✅ Created membership: {user.email} -> {tenant.name} (owner)")
        else:
            print(f"   ℹ️  Membership already exists: {user.email} -> {tenant.name}")
        
        # 5. Create SMS provider (like local)
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
        if created:
            print(f"   ✅ Created SMS provider: {provider.name}")
        else:
            print(f"   ℹ️  SMS provider already exists: {provider.name}")
        
        # 6. Create sender IDs (like local)
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
                print(f"   ✅ Created sender ID: {sender_id.sender_id}")
        
        # 7. Create SMS packages (like local)
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
                print(f"   ✅ Created package: {package.name}")
        
        # 8. Create billing plan
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
        if created:
            print(f"   ✅ Created billing plan: {plan.name}")
        
        # 9. Create subscription
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
        if created:
            print(f"   ✅ Created subscription: {subscription.status}")
        
        # 10. Create SMS balance
        print("💳 Creating SMS balance...")
        balance, created = SMSBalance.objects.get_or_create(
            tenant=tenant,
            defaults={
                'credits': 1000,
                'total_purchased': 1000,
                'total_used': 0
            }
        )
        if created:
            print(f"   ✅ Created SMS balance: {balance.credits} credits")
        
        print("=" * 60)
        print("🎉 Production setup completed successfully!")
        print("=" * 60)
        print(f"📧 Email: {user.email}")
        print(f"🔑 Password: admin123")
        print(f"👤 Name: {user.first_name} {user.last_name}")
        print(f"🏢 Tenant: {tenant.name} ({tenant.subdomain})")
        print(f"🌐 Admin URL: http://104.131.116.55:8000/admin/")
        print("=" * 60)
        
        print("\n📊 Data Created (like local):")
        print(f"  🏢 Tenant: {tenant.name}")
        print(f"  👤 Admin: {user.email}")
        print(f"  👥 Membership: {user.email} -> {tenant.name} (owner)")
        print(f"  📱 SMS Provider: {provider.name}")
        print(f"  📝 Sender IDs: {SMSSenderID.objects.filter(tenant=tenant).count()}")
        print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
        print(f"  📋 Billing Plan: {plan.name}")
        print(f"  💰 SMS Balance: {balance.credits} credits")
        
        print(f"\n✅ Your admin dashboard now has the same data as local development!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_like_local()
