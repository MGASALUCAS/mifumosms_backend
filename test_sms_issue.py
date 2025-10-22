"""
Test script to diagnose SMS sending issue
Run this on the server with: python test_sms_issue.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSBalance
from messaging.models_sms import SMSSenderID
from messaging.services.sms_validation import SMSValidationService
from tenants.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

print("SMS SENDING ISSUE DIAGNOSIS")
print("="*60)

# Find the user by email
try:
    user = User.objects.get(email='mgasa.loucat12@gmail.com')
    tenant = user.tenant
    
    print(f"\n✅ User Found: {user.email}")
    print(f"✅ Tenant Found: {tenant.name}")
    
    # 1. Check SMS Balance
    try:
        balance = SMSBalance.objects.get(tenant=tenant)
        print(f"\n1. SMS Balance Check:")
        print(f"   Credits: {balance.credits}")
        print(f"   Total Purchased: {balance.total_purchased}")
        print(f"   Total Used: {balance.total_used}")
        print(f"   Available: {balance.credits - balance.total_used}")
    except SMSBalance.DoesNotExist:
        print(f"\n1. SMS Balance Check:")
        print(f"   ❌ No SMS Balance found for tenant!")
    
    # 2. Check Sender ID
    print(f"\n2. Sender ID Check:")
    sender_ids = SMSSenderID.objects.filter(tenant=tenant)
    print(f"   Total Sender IDs: {sender_ids.count()}")
    
    for sender in sender_ids:
        print(f"   - Name: {sender.sender_name}")
        print(f"     ID: {sender.id}")
        print(f"     Status: {sender.status}")
        print(f"     Active: {sender.is_active}")
        print()
    
    # Check for "Quantum" specifically
    quantum_sender = SMSSenderID.objects.filter(
        tenant=tenant,
        sender_name__iexact='Quantum'
    ).first()
    
    if quantum_sender:
        print(f"   ✅ 'Quantum' Sender ID Found:")
        print(f"      ID: {quantum_sender.id}")
        print(f"      Status: {quantum_sender.status}")
        print(f"      Active: {quantum_sender.is_active}")
    else:
        print(f"   ❌ 'Quantum' Sender ID NOT Found!")
        print(f"\n   Checking all sender IDs for partial match:")
        for sender in sender_ids:
            if 'quantum' in sender.sender_name.lower():
                print(f"      Found: {sender.sender_name} (status: {sender.status}, active: {sender.is_active})")
    
    # 3. Check SMS Validation
    print(f"\n3. SMS Validation Check:")
    validation_service = SMSValidationService(tenant)
    validation_result = validation_service.validate_sms_sending(
        sender_id='Quantum',
        required_credits=1
    )
    
    print(f"   Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"   Error: {validation_result['error']}")
        print(f"   Error Type: {validation_result.get('error_type', 'unknown')}")
    else:
        print(f"   Available Credits: {validation_result['available_credits']}")
        print(f"   Remaining Credits: {validation_result['remaining_credits']}")
    
    # 4. Check User Tenant
    print(f"\n4. User & Tenant Check:")
    print(f"   User: {user.email}")
    print(f"   Has Tenant: {hasattr(user, 'tenant') and user.tenant is not None}")
    if hasattr(user, 'tenant') and user.tenant:
        print(f"   Tenant Name: {user.tenant.name}")
        print(f"   Tenant ID: {user.tenant.id}")

except User.DoesNotExist:
    print(f"\n❌ User 'mgasa.loucat12@gmail.com' not found!")
    print(f"\nAvailable users:")
    for u in User.objects.all()[:5]:
        print(f"   - {u.email}")

print(f"\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
print(f"\nTo run this on the server, use:")
print(f"  python test_sms_issue.py")

