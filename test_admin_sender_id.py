#!/usr/bin/env python
"""
Test script to verify admin users get default sender ID automatically.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
from billing.models import SMSBalance

User = get_user_model()

def test_admin_sender_id_creation():
    """Test that admin users get default sender ID automatically."""
    
    print("Testing admin user creation with default sender ID...")
    
    # Create a test admin user
    test_email = "testadmin@example.com"
    
    # Clean up any existing test user
    if User.objects.filter(email=test_email).exists():
        print(f"Cleaning up existing test user: {test_email}")
        User.objects.filter(email=test_email).delete()
    
    try:
        # Create admin user - this should trigger the signal
        admin_user = User.objects.create_user(
            email=test_email,
            password="testpass123",
            first_name="Test",
            last_name="Admin",
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        
        print(f"✅ Created admin user: {admin_user.email}")
        
        # Check if tenant was created
        tenant = admin_user.tenant
        if tenant:
            print(f"✅ Tenant created: {tenant.name}")
            
            # Check if SMS provider was created
            sms_providers = SMSProvider.objects.filter(tenant=tenant)
            if sms_providers.exists():
                print(f"✅ SMS provider created: {sms_providers.first().name}")
            else:
                print("❌ No SMS provider found")
            
            # Check if default sender ID was created
            sender_ids = SMSSenderID.objects.filter(tenant=tenant, sender_id="Taarifa-SMS")
            if sender_ids.exists():
                sender_id = sender_ids.first()
                print(f"✅ Default sender ID created: {sender_id.sender_id} (status: {sender_id.status})")
            else:
                print("❌ No default sender ID found")
            
            # Check if SMS balance was created
            sms_balances = SMSBalance.objects.filter(tenant=tenant)
            if sms_balances.exists():
                balance = sms_balances.first()
                print(f"✅ SMS balance created: {balance.credits} credits")
            else:
                print("❌ No SMS balance found")
                
        else:
            print("❌ No tenant found for admin user")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        print("\nCleaning up test data...")
        if User.objects.filter(email=test_email).exists():
            User.objects.filter(email=test_email).delete()
            print("✅ Test data cleaned up")

if __name__ == "__main__":
    test_admin_sender_id_creation()
