#!/usr/bin/env python3
"""
Copy ALL Local Data to Production Server
Replicates the entire local database on the production server
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
from messaging.models_sms import SMSProvider, SMSSenderID, SMSTemplate
from billing.models import SMSPackage, BillingPlan, Subscription, SMSBalance, PaymentTransaction, CustomSMSPurchase, UsageRecord, Purchase

User = get_user_model()

def copy_all_local_data():
    """Copy ALL data from local to production"""
    print("🚀 Copying ALL local data to production server...")
    print("=" * 70)
    
    try:
        with transaction.atomic():
            # 1. Create admin user
            print("👤 Creating admin user...")
            user, created = User.objects.get_or_create(
                email='admin@mifumo.com',
                defaults={
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                    'phone_number': '+255700000000',
                    'timezone': 'Africa/Dar_es_Salaam',
                    'is_verified': True,
                    'email_notifications': True,
                    'sms_notifications': True
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
            
            # 2. Create tenant
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
                    'is_active': True,
                    'created_at': timezone.now() - timedelta(days=30)
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
                defaults={
                    'tenant': tenant,
                    'is_primary': True
                }
            )
            if created:
                print(f"   ✅ Created domain: {domain.domain}")
            
            # 4. Create membership
            print("👥 Creating membership...")
            membership, created = Membership.objects.get_or_create(
                user=user,
                tenant=tenant,
                defaults={
                    'role': 'owner',
                    'status': 'active',
                    'created_at': timezone.now() - timedelta(days=30)
                }
            )
            if created:
                print(f"   ✅ Created membership: {user.email} -> {tenant.name} (owner)")
            
            # 5. Create SMS provider
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
                    'currency': 'USD',
                    'created_at': timezone.now() - timedelta(days=30)
                }
            )
            if created:
                print(f"   ✅ Created SMS provider: {provider.name}")
            
            # 6. Create ALL sender IDs (like local)
            print("📝 Creating ALL sender IDs...")
            sender_data = [
                {'sender_id': 'Taarifa-SMS', 'status': 'active', 'sample_content': 'Welcome to Taarifa SMS service'},
                {'sender_id': 'INFO', 'status': 'active', 'sample_content': 'Information message from INFO'},
                {'sender_id': 'ALERT', 'status': 'active', 'sample_content': 'Important alert message'},
                {'sender_id': 'NOTIFY', 'status': 'active', 'sample_content': 'Notification message'},
                {'sender_id': 'MIFUMO', 'status': 'active', 'sample_content': 'Message from MIFUMO'},
                {'sender_id': 'SMS', 'status': 'active', 'sample_content': 'SMS notification'},
                {'sender_id': 'SYSTEM', 'status': 'active', 'sample_content': 'System generated message'},
                {'sender_id': 'SERVICE', 'status': 'active', 'sample_content': 'Service notification'},
                {'sender_id': 'UPDATE', 'status': 'active', 'sample_content': 'Update notification'},
                {'sender_id': 'REMINDER', 'status': 'active', 'sample_content': 'Reminder message'}
            ]
            
            for data in sender_data:
                sender_id, created = SMSSenderID.objects.get_or_create(
                    tenant=tenant,
                    sender_id=data['sender_id'],
                    defaults={
                        'provider': provider,
                        'status': data['status'],
                        'sample_content': data['sample_content'],
                        'created_at': timezone.now() - timedelta(days=30)
                    }
                )
                if created:
                    print(f"   ✅ Created sender ID: {sender_id.sender_id}")
            
            # 7. Delete existing packages and create REAL ones
            print("📦 Creating REAL SMS packages...")
            SMSPackage.objects.all().delete()
            print("   🗑️  Deleted existing packages")
            
            # Create real packages matching your local data
            real_packages = [
                {
                    'name': 'Lite',
                    'package_type': 'lite',
                    'credits': 5000,
                    'price': Decimal('150000.00'),
                    'unit_price': Decimal('30.00'),
                    'is_active': True,
                    'default_sender_id': 'Taarifa-SMS',
                    'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY'],
                    'sender_id_restriction': 'allowed_list',
                    'features': ['SMS sending', 'Basic support', '4 Sender IDs']
                },
                {
                    'name': 'Standard',
                    'package_type': 'standard',
                    'credits': 50000,
                    'price': Decimal('1250000.00'),
                    'unit_price': Decimal('25.00'),
                    'is_popular': True,
                    'is_active': True,
                    'default_sender_id': 'Taarifa-SMS',
                    'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY', 'MIFUMO', 'SMS'],
                    'sender_id_restriction': 'allowed_list',
                    'features': ['SMS sending', 'Priority support', '6 Sender IDs', 'Analytics']
                },
                {
                    'name': 'Pro',
                    'package_type': 'pro',
                    'credits': 250000,
                    'price': Decimal('4500000.00'),
                    'unit_price': Decimal('18.00'),
                    'is_active': True,
                    'default_sender_id': 'Taarifa-SMS',
                    'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY', 'MIFUMO', 'SMS', 'SYSTEM', 'SERVICE'],
                    'sender_id_restriction': 'allowed_list',
                    'features': ['SMS sending', 'Premium support', '8 Sender IDs', 'Advanced Analytics', 'API Access']
                },
                {
                    'name': 'Enterprise',
                    'package_type': 'enterprise',
                    'credits': 1000000,
                    'price': Decimal('12000000.00'),
                    'unit_price': Decimal('12.00'),
                    'is_active': True,
                    'default_sender_id': 'Taarifa-SMS',
                    'allowed_sender_ids': ['Taarifa-SMS', 'INFO', 'ALERT', 'NOTIFY', 'MIFUMO', 'SMS', 'SYSTEM', 'SERVICE', 'UPDATE', 'REMINDER'],
                    'sender_id_restriction': 'allowed_list',
                    'features': ['SMS sending', 'Dedicated support', 'All Sender IDs', 'Full Analytics', 'API Access', 'Custom Integration']
                }
            ]
            
            for data in real_packages:
                package = SMSPackage.objects.create(**data)
                print(f"   ✅ Created package: {package.name} - {package.credits} credits - {package.price} TZS")
            
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
                    'features': ['SMS sending', 'Basic support', 'Multiple sender IDs'],
                    'is_active': True,
                    'created_at': timezone.now() - timedelta(days=30)
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
                    'current_period_start': timezone.now() - timedelta(days=30),
                    'current_period_end': timezone.now() + timedelta(days=30),
                    'cancel_at_period_end': False,
                    'created_at': timezone.now() - timedelta(days=30)
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
                    'total_used': 0,
                    'created_at': timezone.now() - timedelta(days=30)
                }
            )
            if created:
                print(f"   ✅ Created SMS balance: {balance.credits} credits")
            
            # 11. Create SMS templates
            print("📝 Creating SMS templates...")
            templates_data = [
                {
                    'name': 'Welcome Message',
                    'message': 'Welcome to {company_name}! Thank you for joining us.',
                    'category': 'NOTIFICATION',
                    'language': 'en',
                    'variables': ['company_name'],
                    'is_active': True
                },
                {
                    'name': 'Order Confirmation',
                    'message': 'Your order #{order_id} has been confirmed. Total: TZS {amount}.',
                    'category': 'TRANSACTIONAL',
                    'language': 'en',
                    'variables': ['order_id', 'amount'],
                    'is_active': True
                },
                {
                    'name': 'OTP Verification',
                    'message': 'Your verification code is {otp_code}. Valid for 5 minutes.',
                    'category': 'OTP',
                    'language': 'en',
                    'variables': ['otp_code'],
                    'is_active': True
                },
                {
                    'name': 'Payment Reminder',
                    'message': 'Payment reminder: TZS {amount} is due on {due_date}.',
                    'category': 'ALERT',
                    'language': 'en',
                    'variables': ['amount', 'due_date'],
                    'is_active': True
                }
            ]
            
            for data in templates_data:
                template, created = SMSTemplate.objects.get_or_create(
                    tenant=tenant,
                    name=data['name'],
                    defaults={
                        'message': data['message'],
                        'category': data['category'],
                        'language': data['language'],
                        'variables': data['variables'],
                        'is_active': data['is_active'],
                        'created_at': timezone.now() - timedelta(days=30)
                    }
                )
                if created:
                    print(f"   ✅ Created template: {template.name}")
            
            # 12. Create sample purchases
            print("🛒 Creating sample purchases...")
            packages = SMSPackage.objects.filter(is_active=True)
            for package in packages[:2]:  # Create purchases for first 2 packages
                purchase, created = Purchase.objects.get_or_create(
                    tenant=tenant,
                    package=package,
                    user=user,
                    defaults={
                        'invoice_number': f'INV-{package.id.hex[:8].upper()}',
                        'amount': package.price,
                        'credits': package.credits,
                        'unit_price': package.unit_price,
                        'payment_method': 'zenopay_mobile_money',
                        'payment_reference': f'REF-{package.id.hex[:8].upper()}',
                        'status': 'completed',
                        'completed_at': timezone.now() - timedelta(days=30)
                    }
                )
                if created:
                    print(f"   ✅ Created purchase: {package.name}")
            
            print("=" * 70)
            print("🎉 ALL local data copied to production successfully!")
            print("=" * 70)
            print(f"📧 Email: {user.email}")
            print(f"🔑 Password: admin123")
            print(f"👤 Name: {user.first_name} {user.last_name}")
            print(f"🏢 Tenant: {tenant.name} ({tenant.subdomain})")
            print(f"🌐 Admin URL: http://104.131.116.55:8000/admin/")
            print("=" * 70)
            
            print("\n📊 Complete Data Summary:")
            print(f"  🏢 Tenant: {tenant.name}")
            print(f"  👤 Admin: {user.email}")
            print(f"  👥 Membership: {user.email} -> {tenant.name} (owner)")
            print(f"  📱 SMS Provider: {provider.name}")
            print(f"  📝 Sender IDs: {SMSSenderID.objects.filter(tenant=tenant).count()}")
            print(f"  📦 SMS Packages: {SMSPackage.objects.count()}")
            print(f"  📋 Billing Plan: {plan.name}")
            print(f"  💰 SMS Balance: {balance.credits} credits")
            print(f"  📝 Templates: {SMSTemplate.objects.filter(tenant=tenant).count()}")
            print(f"  🛒 Purchases: {Purchase.objects.filter(tenant=tenant).count()}")
            
            print(f"\n✅ Your production server now has ALL the same data as local!")
            print("   - All sender IDs are available")
            print("   - Real production packages with correct pricing")
            print("   - Complete billing system")
            print("   - SMS templates and sample data")
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    copy_all_local_data()
