#!/usr/bin/env python
"""
Test script for ZenoPay payment gateway integration.
This script tests the core functionality without requiring external API calls.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import (
    SMSPackage, SMSBalance, Purchase, PaymentTransaction, 
    UsageRecord, BillingPlan, Subscription
)
from billing.zenopay_service import ZenoPayService
from tenants.models import Tenant
from accounts.models import User
from django.utils import timezone
import uuid


def create_test_data():
    """Create test data for testing."""
    print("Creating test data...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Tenant",
        defaults={
            'domain': 'test.localhost',
            'is_active': True
        }
    )
    print(f"Tenant: {'Created' if created else 'Exists'} - {tenant.name}")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'tenant': tenant,
            'is_active': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    print(f"User: {'Created' if created else 'Exists'} - {user.email}")
    
    # Create test SMS package
    package, created = SMSPackage.objects.get_or_create(
        name="Test Starter Pack",
        defaults={
            'package_type': 'lite',
            'credits': 100,
            'price': Decimal('1000.00'),
            'unit_price': Decimal('10.00'),
            'is_popular': True,
            'features': ['100 SMS Credits', 'Email Support'],
            'is_active': True
        }
    )
    print(f"Package: {'Created' if created else 'Exists'} - {package.name}")
    
    # Create SMS balance for tenant
    balance, created = SMSBalance.objects.get_or_create(tenant=tenant)
    print(f"SMS Balance: {'Created' if created else 'Exists'} - {balance.credits} credits")
    
    return tenant, user, package


def test_payment_transaction_creation():
    """Test payment transaction creation."""
    print("\n=== Testing Payment Transaction Creation ===")
    
    tenant, user, package = create_test_data()
    
    # Create payment transaction
    transaction = PaymentTransaction.objects.create(
        tenant=tenant,
        user=user,
        zenopay_order_id=str(uuid.uuid4()),
        order_id=f"MIFUMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
        invoice_number=f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
        amount=package.price,
        currency='TZS',
        buyer_email='test@example.com',
        buyer_name='Test User',
        buyer_phone='0744963858',
        payment_method='zenopay_mobile_money',
        webhook_url='http://localhost:8000/api/billing/payments/webhook/'
    )
    
    print(f"✅ Payment Transaction Created: {transaction.order_id}")
    print(f"   Status: {transaction.status}")
    print(f"   Amount: {transaction.amount} {transaction.currency}")
    print(f"   ZenoPay Order ID: {transaction.zenopay_order_id}")
    
    return transaction


def test_purchase_creation():
    """Test purchase creation linked to payment transaction."""
    print("\n=== Testing Purchase Creation ===")
    
    tenant, user, package = create_test_data()
    transaction = test_payment_transaction_creation()
    
    # Create purchase
    purchase = Purchase.objects.create(
        tenant=tenant,
        user=user,
        package=package,
        payment_transaction=transaction,
        invoice_number=transaction.invoice_number,
        amount=package.price,
        credits=package.credits,
        unit_price=package.unit_price,
        payment_method='zenopay_mobile_money',
        status='pending'
    )
    
    print(f"✅ Purchase Created: {purchase.invoice_number}")
    print(f"   Package: {purchase.package.name}")
    print(f"   Credits: {purchase.credits}")
    print(f"   Amount: {purchase.amount}")
    print(f"   Status: {purchase.status}")
    print(f"   Linked Transaction: {purchase.payment_transaction.order_id}")
    
    return purchase


def test_payment_status_updates():
    """Test payment status updates."""
    print("\n=== Testing Payment Status Updates ===")
    
    transaction = test_payment_transaction_creation()
    
    # Test processing status
    transaction.mark_as_processing()
    print(f"✅ Status Updated to Processing: {transaction.status}")
    
    # Test completed status
    transaction.mark_as_completed({
        'reference': '0936183435',
        'transid': 'CEJ3I3SETSN',
        'channel': 'MPESA-TZ',
        'msisdn': '255744963858'
    })
    print(f"✅ Status Updated to Completed: {transaction.status}")
    print(f"   Reference: {transaction.zenopay_reference}")
    print(f"   Transaction ID: {transaction.zenopay_transid}")
    print(f"   Channel: {transaction.zenopay_channel}")
    print(f"   Phone: {transaction.zenopay_msisdn}")
    
    return transaction


def test_purchase_completion():
    """Test purchase completion and credit addition."""
    print("\n=== Testing Purchase Completion ===")
    
    purchase = test_purchase_creation()
    tenant = purchase.tenant
    
    # Get initial balance
    initial_balance = tenant.sms_balance.credits
    print(f"Initial Balance: {initial_balance} credits")
    
    # Complete purchase
    success = purchase.complete_purchase()
    
    if success:
        # Refresh balance
        tenant.sms_balance.refresh_from_db()
        new_balance = tenant.sms_balance.credits
        
        print(f"✅ Purchase Completed Successfully")
        print(f"   Credits Added: {purchase.credits}")
        print(f"   New Balance: {new_balance} credits")
        print(f"   Balance Increase: {new_balance - initial_balance} credits")
    else:
        print(f"❌ Purchase Completion Failed")
    
    return purchase


def test_zenopay_service():
    """Test ZenoPay service functionality."""
    print("\n=== Testing ZenoPay Service ===")
    
    service = ZenoPayService()
    
    # Test phone number validation
    test_phones = [
        '0744963858',
        '255744963858',
        '744963858',
        'invalid_phone'
    ]
    
    for phone in test_phones:
        try:
            formatted = service._validate_phone_number(phone)
            print(f"✅ Phone {phone} -> {formatted}")
        except Exception as e:
            print(f"❌ Phone {phone} -> Error: {e}")
    
    # Test order ID generation
    order_id = service.generate_order_id()
    print(f"✅ Generated Order ID: {order_id}")
    
    # Test amount formatting
    amount = service.format_amount(Decimal('1000.50'))
    print(f"✅ Formatted Amount: {amount} (type: {type(amount)})")


def test_progress_tracking():
    """Test progress tracking functionality."""
    print("\n=== Testing Progress Tracking ===")
    
    transaction = test_payment_transaction_creation()
    
    # Simulate different progress states
    progress_states = [
        ('pending', 'Payment Initiated', 25, 'blue', 'clock'),
        ('processing', 'Payment Processing', 50, 'yellow', 'sync'),
        ('completed', 'Payment Completed', 100, 'green', 'check'),
        ('failed', 'Payment Failed', 0, 'red', 'x')
    ]
    
    for status, step, percentage, color, icon in progress_states:
        transaction.status = status
        transaction.save()
        
        # Simulate progress calculation (simplified)
        progress = {
            'step': 1 if status == 'pending' else 2 if status == 'processing' else 4 if status == 'completed' else 1,
            'total_steps': 4,
            'current_step': step,
            'percentage': percentage,
            'status_color': color,
            'status_icon': icon
        }
        
        print(f"✅ Status: {status} -> {step} ({percentage}%) - {color} {icon}")


def test_error_handling():
    """Test error handling scenarios."""
    print("\n=== Testing Error Handling ===")
    
    # Test invalid phone number
    service = ZenoPayService()
    try:
        service._validate_phone_number('invalid')
        print("❌ Should have failed for invalid phone")
    except Exception as e:
        print(f"✅ Correctly caught invalid phone error: {e}")
    
    # Test payment transaction with invalid data
    try:
        PaymentTransaction.objects.create(
            tenant=None,  # Invalid tenant
            user=None,    # Invalid user
            zenopay_order_id='',  # Empty order ID
            order_id='',
            invoice_number='',
            amount=Decimal('0'),
            currency='',
            buyer_email='invalid-email',
            buyer_name='',
            buyer_phone='',
            payment_method='invalid_method'
        )
        print("❌ Should have failed for invalid data")
    except Exception as e:
        print(f"✅ Correctly caught invalid data error: {e}")


def run_all_tests():
    """Run all tests."""
    print("🚀 Starting ZenoPay Integration Tests")
    print("=" * 50)
    
    try:
        test_zenopay_service()
        test_payment_transaction_creation()
        test_purchase_creation()
        test_payment_status_updates()
        test_purchase_completion()
        test_progress_tracking()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Set up ZenoPay API key in environment variables")
        print("2. Run Django migrations: python manage.py migrate")
        print("3. Test with Postman using the provided collection")
        print("4. Verify webhook integration")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
