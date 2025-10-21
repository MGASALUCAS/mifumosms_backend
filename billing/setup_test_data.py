#!/usr/bin/env python
"""
Setup test data for billing API tests.
This script creates sample data that matches the documentation examples.
"""
import os
import sys
import django
from decimal import Decimal
from django.utils import timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from billing.models import (
    SMSPackage, SMSBalance, Purchase, PaymentTransaction, 
    BillingPlan, Subscription, UsageRecord, CustomSMSPurchase
)
from tenants.models import Tenant

User = get_user_model()

def create_test_data():
    """Create comprehensive test data for billing API."""
    print("🔧 Setting up test data for billing API...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name='Test Company',
        defaults={'domain': 'test.com'}
    )
    if created:
        print("✅ Created test tenant")
    else:
        print("ℹ️  Test tenant already exists")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'tenant': tenant
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("ℹ️  Test user already exists")
    
    # Create SMS packages
    packages_data = [
        {
            'name': 'Lite Package',
            'package_type': 'lite',
            'credits': 1000,
            'price': Decimal('25000.00'),
            'unit_price': Decimal('25.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['1000 SMS Credits', 'Standard Support', 'Basic Analytics'],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'Quantum'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Standard Package',
            'package_type': 'standard',
            'credits': 5000,
            'price': Decimal('100000.00'),
            'unit_price': Decimal('20.00'),
            'is_popular': True,
            'is_active': True,
            'features': ['5000 SMS Credits', 'Priority Support', 'Advanced Analytics', 'Bulk SMS Tools'],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'Quantum', 'Mifumo'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Pro Package',
            'package_type': 'pro',
            'credits': 10000,
            'price': Decimal('150000.00'),
            'unit_price': Decimal('15.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['10000 SMS Credits', 'Premium Support', 'Advanced Analytics', 'Bulk SMS Tools', 'API Access'],
            'default_sender_id': 'Mifumo',
            'allowed_sender_ids': ['Mifumo', 'Quantum', 'Taarifa-SMS'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Enterprise Package',
            'package_type': 'enterprise',
            'credits': 50000,
            'price': Decimal('500000.00'),
            'unit_price': Decimal('10.00'),
            'is_popular': False,
            'is_active': True,
            'features': ['50000 SMS Credits', 'Enterprise Support', 'Advanced Analytics', 'Bulk SMS Tools', 'API Access', 'Custom Integration'],
            'default_sender_id': 'Mifumo',
            'allowed_sender_ids': ['Mifumo', 'Quantum', 'Taarifa-SMS', 'CustomSender'],
            'sender_id_restriction': 'allowed_list'
        }
    ]
    
    for package_data in packages_data:
        package, created = SMSPackage.objects.get_or_create(
            name=package_data['name'],
            defaults=package_data
        )
        if created:
            print(f"✅ Created SMS package: {package.name}")
        else:
            print(f"ℹ️  SMS package already exists: {package.name}")
    
    # Create billing plan
    billing_plan, created = BillingPlan.objects.get_or_create(
        name='Professional',
        defaults={
            'plan_type': 'professional',
            'description': 'Professional plan with advanced features',
            'price': Decimal('50000.00'),
            'currency': 'TZS',
            'billing_cycle': 'monthly',
            'max_contacts': 10000,
            'max_campaigns': 100,
            'max_sms_per_month': 5000,
            'features': ['Advanced Analytics', 'Priority Support', 'Bulk SMS Tools', 'Custom Sender IDs'],
            'is_active': True
        }
    )
    if created:
        print("✅ Created billing plan")
    else:
        print("ℹ️  Billing plan already exists")
    
    # Create subscription
    subscription, created = Subscription.objects.get_or_create(
        tenant=tenant,
        defaults={
            'plan': billing_plan,
            'status': 'active',
            'current_period_start': timezone.now().replace(day=1),
            'current_period_end': timezone.now().replace(day=1) + timezone.timedelta(days=30),
            'cancel_at_period_end': False
        }
    )
    if created:
        print("✅ Created subscription")
    else:
        print("ℹ️  Subscription already exists")
    
    # Create SMS balance
    sms_balance, created = SMSBalance.objects.get_or_create(
        tenant=tenant,
        defaults={
            'credits': 1500,
            'total_purchased': 10000,
            'total_used': 8500
        }
    )
    if created:
        print("✅ Created SMS balance")
    else:
        print("ℹ️  SMS balance already exists")
    
    # Create sample purchases
    standard_package = SMSPackage.objects.get(name='Standard Package')
    pro_package = SMSPackage.objects.get(name='Pro Package')
    
    purchases_data = [
        {
            'package': standard_package,
            'amount': Decimal('100000.00'),
            'credits': 5000,
            'unit_price': Decimal('20.00'),
            'payment_method': 'zenopay_mobile_money',
            'payment_reference': 'MPESA123456789',
            'status': 'completed',
            'completed_at': timezone.now() - timezone.timedelta(days=5)
        },
        {
            'package': pro_package,
            'amount': Decimal('150000.00'),
            'credits': 10000,
            'unit_price': Decimal('15.00'),
            'payment_method': 'zenopay_mobile_money',
            'payment_reference': 'MPESA987654321',
            'status': 'completed',
            'completed_at': timezone.now() - timezone.timedelta(days=2)
        }
    ]
    
    for purchase_data in purchases_data:
        purchase, created = Purchase.objects.get_or_create(
            tenant=tenant,
            package=purchase_data['package'],
            amount=purchase_data['amount'],
            defaults=purchase_data
        )
        if created:
            print(f"✅ Created purchase: {purchase.package.name}")
        else:
            print(f"ℹ️  Purchase already exists: {purchase.package.name}")
    
    # Create sample usage records
    now = timezone.now()
    usage_records_data = [
        {
            'credits_used': 100,
            'cost': Decimal('2500.00'),
            'created_at': now
        },
        {
            'credits_used': 200,
            'cost': Decimal('5000.00'),
            'created_at': now - timezone.timedelta(days=1)
        },
        {
            'credits_used': 150,
            'cost': Decimal('3750.00'),
            'created_at': now - timezone.timedelta(days=7)
        },
        {
            'credits_used': 300,
            'cost': Decimal('7500.00'),
            'created_at': now - timezone.timedelta(days=30)
        }
    ]
    
    for usage_data in usage_records_data:
        usage_record, created = UsageRecord.objects.get_or_create(
            tenant=tenant,
            credits_used=usage_data['credits_used'],
            cost=usage_data['cost'],
            created_at=usage_data['created_at'],
            defaults=usage_data
        )
        if created:
            print(f"✅ Created usage record: {usage_record.credits_used} credits")
        else:
            print(f"ℹ️  Usage record already exists: {usage_record.credits_used} credits")
    
    # Create sample payment transactions
    payment_transactions_data = [
        {
            'order_id': 'MIFUMO-20241201-ABC12345',
            'amount': Decimal('100000.00'),
            'currency': 'TZS',
            'status': 'completed',
            'payment_reference': 'MPESA123456789',
            'provider': 'vodacom',
            'completed_at': timezone.now() - timezone.timedelta(days=5)
        },
        {
            'order_id': 'MIFUMO-20241201-DEF67890',
            'amount': Decimal('50000.00'),
            'currency': 'TZS',
            'status': 'pending',
            'provider': 'tigo'
        }
    ]
    
    for transaction_data in payment_transactions_data:
        transaction, created = PaymentTransaction.objects.get_or_create(
            tenant=tenant,
            order_id=transaction_data['order_id'],
            defaults=transaction_data
        )
        if created:
            print(f"✅ Created payment transaction: {transaction.order_id}")
        else:
            print(f"ℹ️  Payment transaction already exists: {transaction.order_id}")
    
    print("\n🎉 Test data setup completed!")
    print("\n📊 Summary:")
    print(f"  - Tenant: {tenant.name}")
    print(f"  - User: {user.email}")
    print(f"  - SMS Packages: {SMSPackage.objects.count()}")
    print(f"  - Billing Plans: {BillingPlan.objects.count()}")
    print(f"  - Subscriptions: {Subscription.objects.count()}")
    print(f"  - SMS Balances: {SMSBalance.objects.count()}")
    print(f"  - Purchases: {Purchase.objects.count()}")
    print(f"  - Usage Records: {UsageRecord.objects.count()}")
    print(f"  - Payment Transactions: {PaymentTransaction.objects.count()}")
    
    print("\n🚀 You can now run the tests:")
    print("  python test_billing_api.py")

if __name__ == '__main__':
    create_test_data()
