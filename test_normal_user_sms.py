#!/usr/bin/env python
"""
Test script for normal user SMS functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from tenants.models import Tenant, Membership
from messaging.models_sms import SMSSenderID, SMSProvider
from messaging.services.sms_validation import SMSValidationService
from messaging.services.beem_sms import BeemSMSService
from billing.models import SMSBalance, SMSPackage, Purchase, UsageRecord
from messaging.models_sender_requests import SenderIDRequest
import logging

User = get_user_model()

def create_test_user():
    """Create a test normal user with 2 SMS credits"""
    
    # Create or get tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Normal User Organization",
        defaults={
            'subdomain': 'test-normal-user',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created new tenant: {tenant.name}")
    else:
        print(f"Using existing tenant: {tenant.name}")
    
    # Create normal user
    user, created = User.objects.get_or_create(
        email="normaluser@test.com",
        defaults={
            'first_name': 'Normal',
            'last_name': 'User',
            'is_staff': False,
            'is_active': True
        }
    )
    
    if created:
        print(f"Created new normal user: {user.email}")
    else:
        print(f"Using existing user: {user.email}")
    
    # Create membership to link user to tenant
    membership, created = Membership.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={
            'role': 'owner',
            'status': 'active',
            'joined_at': timezone.now()
        }
    )
    
    if created:
        print(f"Created membership for user in tenant")
    else:
        print(f"Membership already exists")
    
    # Create SMS balance with 2 credits
    sms_balance, created = SMSBalance.objects.get_or_create(
        tenant=tenant,
        defaults={
            'credits': 2,
            'total_purchased': 0  # No purchases yet
        }
    )
    
    if created:
        print(f"Created SMS balance with 2 credits")
    else:
        sms_balance.credits = 2
        sms_balance.total_purchased = 0
        sms_balance.save()
        print(f"Reset SMS balance to 2 credits")
    
    # Create Beem provider for tenant
    provider, created = SMSProvider.objects.get_or_create(
        tenant=tenant,
        provider_type='beem',
        defaults={
            'name': 'Beem Africa SMS',
            'api_key': '',
            'secret_key': '',
            'api_url': 'https://apisms.beem.africa/v1/send',
            'is_active': True,
            'is_default': True,
            'cost_per_sms': 0.05,
            'currency': 'USD'
        }
    )
    
    if created:
        print(f"Created Beem provider for tenant")
    else:
        print(f"Using existing Beem provider")
    
    # Create Taarifa-SMS sender ID for tenant
    sender_id, created = SMSSenderID.objects.get_or_create(
        tenant=tenant,
        sender_id='Taarifa-SMS',
        defaults={
            'provider': provider,
            'sample_content': 'A test use case for the sender name purposely used for information transfer.',
            'status': 'active'
        }
    )
    
    if created:
        print(f"Created Taarifa-SMS sender ID")
    else:
        print(f"Using existing Taarifa-SMS sender ID")
        # Update the existing sender ID to be active
        sender_id.status = 'active'
        sender_id.save()
    
    return user, tenant, sms_balance, sender_id

def test_purchase_history(user, tenant):
    """Test that purchase history is empty for new user"""
    
    print("\n=== Testing Purchase History ===")
    
    # Check purchases
    purchases = Purchase.objects.filter(tenant=tenant)
    print(f"Purchase count: {purchases.count()}")
    
    if purchases.count() == 0:
        print("Purchase history is empty (correct for new user)")
    else:
        print("Purchase history is not empty")
        for purchase in purchases:
            print(f"  - Purchase: {purchase.package.name} - {purchase.amount} credits")
    
    # Check usage records
    usage_records = UsageRecord.objects.filter(tenant=tenant)
    print(f"Usage record count: {usage_records.count()}")
    
    if usage_records.count() == 0:
        print("Usage records are empty (correct for new user)")
    else:
        print("Usage records are not empty")
        for usage in usage_records:
            print(f"  - Usage: {usage.description} - {usage.amount} credits")

def test_sender_id_request(user, tenant):
    """Test sender ID request functionality"""
    
    print("\n=== Testing Sender ID Request ===")
    
    # Check existing sender ID requests
    requests = SenderIDRequest.objects.filter(tenant=tenant)
    print(f"Existing sender ID requests: {requests.count()}")
    
    # Create or get existing sender ID request
    request_data = {
        'request_type': 'default',
        'requested_sender_id': 'Taarifa-SMS',
        'sample_content': 'A test use case for the sender name purposely used for information transfer.',
        'business_justification': 'Testing sender ID request functionality for normal user.'
    }
    
    sender_request, created = SenderIDRequest.objects.get_or_create(
        tenant=tenant,
        requested_sender_id='Taarifa-SMS',
        defaults={
            'user': user,
            **request_data
        }
    )
    
    if created:
        print(f"Created sender ID request: {sender_request.id}")
    else:
        print(f"Using existing sender ID request: {sender_request.id}")
    
    print(f"Request status: {sender_request.status}")
    
    # Auto-approve the request (simulating admin approval)
    try:
        sender_request.approve(user)
        print(f"Approved sender ID request. New status: {sender_request.status}")
    except Exception as e:
        print(f"Could not approve request (sender ID may already exist): {e}")
        # Mark as approved anyway for testing
        sender_request.status = 'approved'
        sender_request.save()
    
    return sender_request

def test_sms_sending(user, tenant, sms_balance, sender_id):
    """Test SMS sending with credit deduction"""
    
    print("\n=== Testing SMS Sending ===")
    
    # Check initial balance
    print(f"Initial SMS balance: {sms_balance.credits} credits")
    
    # Test message
    message = "Hello! This is a test SMS from a normal user via Mifumo SMS system. Credits are working correctly!"
    phone_number = "255757347863"  # Tanzanian number format
    
    print(f"Message: {message}")
    print(f"Phone: {phone_number}")
    
    # Initialize SMS service
    beem_service = BeemSMSService()
    
    # Check if we can send (validation)
    validation_service = SMSValidationService(tenant)
    validation_result = validation_service.validate_sms_sending(
        sender_id.sender_id,
        required_credits=1
    )
    
    if not validation_result['valid']:
        print(f"Validation failed: {validation_result['error']}")
        return False
    
    print("Validation passed - can send SMS")
    
    # Send SMS
    print("Sending SMS...")
    try:
        response = beem_service.send_sms(
            message=message,
            recipients=[phone_number],
            source_addr=sender_id.sender_id
        )
        
        if response.get('success'):
            print("SMS sent successfully!")
            print(f"Response: {response}")
            
            # Deduct credits
            try:
                validation_service.deduct_credits(
                    amount=1,
                    sender_id=sender_id.sender_id,
                    message_id="normal_user_test_001",
                    description=f"Test SMS from normal user to {phone_number}"
                )
                print("Credits deducted successfully!")
                
                # Check new balance
                sms_balance.refresh_from_db()
                print(f"New SMS balance: {sms_balance.credits} credits")
                
                return True
                
            except Exception as e:
                print(f"Failed to deduct credits: {e}")
                return False
        else:
            print(f"SMS sending failed: {response}")
            return False
            
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def test_second_sms(user, tenant, sms_balance, sender_id):
    """Test sending a second SMS to verify credit system"""
    
    print("\n=== Testing Second SMS ===")
    
    # Check current balance
    print(f"Current SMS balance: {sms_balance.credits} credits")
    
    if sms_balance.credits < 1:
        print("Insufficient credits for second SMS")
        return False
    
    # Test message
    message = "This is the second test SMS! Credit system is working perfectly. Balance should be reduced by 1 more credit."
    phone_number = "255757347863"
    
    print(f"Message: {message}")
    print(f"Phone: {phone_number}")
    
    # Initialize SMS service
    beem_service = BeemSMSService()
    
    # Send SMS
    print("Sending second SMS...")
    try:
        response = beem_service.send_sms(
            message=message,
            recipients=[phone_number],
            source_addr=sender_id.sender_id
        )
        
        if response.get('success'):
            print("Second SMS sent successfully!")
            print(f"Response: {response}")
            
            # Deduct credits
            validation_service = SMSValidationService(tenant)
            validation_service.deduct_credits(
                amount=1,
                sender_id=sender_id.sender_id,
                message_id="normal_user_test_002",
                description=f"Second test SMS from normal user to {phone_number}"
            )
            print("Credits deducted for second SMS!")
            
            # Check final balance
            sms_balance.refresh_from_db()
            print(f"Final SMS balance: {sms_balance.credits} credits")
            
            return True
        else:
            print(f"Second SMS sending failed: {response}")
            return False
            
    except Exception as e:
        print(f"Error sending second SMS: {e}")
        return False

def test_insufficient_credits(user, tenant, sms_balance, sender_id):
    """Test behavior when credits are insufficient"""
    
    print("\n=== Testing Insufficient Credits ===")
    
    # Check current balance
    print(f"Current SMS balance: {sms_balance.credits} credits")
    
    if sms_balance.credits > 0:
        print("Still have credits, cannot test insufficient credits scenario")
        return False
    
    # Try to send SMS
    message = "This should fail due to insufficient credits"
    phone_number = "255757347863"
    
    print(f"Attempting to send SMS with insufficient credits...")
    
    validation_service = SMSValidationService(tenant)
    validation_result = validation_service.validate_sms_sending(
        sender_id.sender_id,
        required_credits=1
    )
    
    if not validation_result['valid']:
        print(f"Validation correctly failed: {validation_result['error']}")
        return True
    else:
        print("Validation should have failed but didn't")
        return False

def main():
    """Main test function"""
    
    print("Starting Normal User SMS Test")
    print("=" * 50)
    
    # Create test user and setup
    user, tenant, sms_balance, sender_id = create_test_user()
    
    # Test purchase history (should be empty)
    test_purchase_history(user, tenant)
    
    # Test sender ID request
    sender_request = test_sender_id_request(user, tenant)
    
    # Test first SMS
    first_sms_success = test_sms_sending(user, tenant, sms_balance, sender_id)
    
    if first_sms_success:
        # Test second SMS
        second_sms_success = test_second_sms(user, tenant, sms_balance, sender_id)
        
        if second_sms_success:
            # Test insufficient credits
            test_insufficient_credits(user, tenant, sms_balance, sender_id)
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"Final SMS balance: {sms_balance.credits} credits")
    print(f"User: {user.email}")
    print(f"Tenant: {tenant.name}")

if __name__ == "__main__":
    main()
