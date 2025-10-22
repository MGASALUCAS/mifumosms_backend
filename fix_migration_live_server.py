#!/usr/bin/env python3
"""
Live Server Migration Fix - Sender ID Issue
Run this script to fix the migration issue and complete the sender ID setup
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID
from messaging.models_sender_requests import SenderIDRequest
from tenants.models import Tenant

User = get_user_model()

def fix_sender_id_migration():
    """Fix the sender ID migration issue."""
    print("🔧 Fixing Sender ID Migration Issue")
    print("=" * 50)
    
    # 1. Check current state
    print("\n1. Checking current state:")
    tenants = Tenant.objects.all()
    print(f"   Total tenants: {tenants.count()}")
    
    taarifa_senders = SMSSenderID.objects.filter(sender_id='Taarifa-SMS')
    print(f"   Taarifa-SMS sender IDs: {taarifa_senders.count()}")
    
    taarifa_requests = SenderIDRequest.objects.filter(requested_sender_id='Taarifa-SMS')
    print(f"   Taarifa-SMS requests: {taarifa_requests.count()}")
    
    # 2. Fix missing sender IDs
    print("\n2. Fixing missing sender IDs:")
    fixed_count = 0
    
    for tenant in tenants:
        # Check if tenant has Taarifa-SMS sender ID
        existing_sender = SMSSenderID.objects.filter(
            tenant=tenant,
            sender_id='Taarifa-SMS'
        ).first()
        
        if not existing_sender:
            print(f"   Creating sender ID for tenant: {tenant.name}")
            
            # Get or create SMS provider
            from messaging.models_sms import SMSProvider
            sms_provider = SMSProvider.objects.filter(
                tenant=tenant,
                is_active=True
            ).first()
            
            if not sms_provider:
                # Create default SMS provider
                owner = tenant.memberships.filter(role='owner').first()
                if owner:
                    sms_provider = SMSProvider.objects.create(
                        tenant=tenant,
                        name="Default Beem Provider",
                        provider_type="beem",
                        is_active=True,
                        is_default=True,
                        api_key="",  # Will be configured later
                        secret_key="",  # Will be configured later
                        api_url="https://apisms.beem.africa/v1/send",
                        cost_per_sms=0.0,
                        currency="TZS",
                        created_by=owner.user
                    )
                    print(f"     Created SMS provider")
                else:
                    print(f"     No owner found, skipping")
                    continue
            
            # Create sender ID
            sender_id = SMSSenderID.objects.create(
                tenant=tenant,
                sender_id="Taarifa-SMS",
                provider=sms_provider,
                status='active',
                sample_content="A test use case for the sender name purposely used for information transfer.",
                created_by=sms_provider.created_by
            )
            print(f"     Created sender ID: {sender_id.sender_id}")
            fixed_count += 1
        else:
            print(f"   Tenant {tenant.name} already has sender ID")
    
    print(f"\n   Fixed {fixed_count} missing sender IDs")
    
    # 3. Fix missing sender ID requests
    print("\n3. Fixing missing sender ID requests:")
    request_fixed_count = 0
    
    for tenant in tenants:
        # Check if tenant has Taarifa-SMS request
        existing_request = SenderIDRequest.objects.filter(
            tenant=tenant,
            requested_sender_id='Taarifa-SMS'
        ).first()
        
        if not existing_request:
            # Get owner to create request
            owner = tenant.memberships.filter(role='owner').first()
            if owner:
                request = SenderIDRequest.objects.create(
                    tenant=tenant,
                    user=owner.user,
                    request_type='default',
                    requested_sender_id='Taarifa-SMS',
                    sample_content="A test use case for the sender name purposely used for information transfer.",
                    status='approved'
                )
                print(f"   Created request for tenant: {tenant.name}")
                request_fixed_count += 1
            else:
                print(f"   No owner found for tenant: {tenant.name}")
        else:
            print(f"   Tenant {tenant.name} already has request")
    
    print(f"\n   Fixed {request_fixed_count} missing requests")
    
    # 4. Final verification
    print("\n4. Final verification:")
    final_senders = SMSSenderID.objects.filter(sender_id='Taarifa-SMS', status='active')
    final_requests = SenderIDRequest.objects.filter(requested_sender_id='Taarifa-SMS', status='approved')
    
    print(f"   Active Taarifa-SMS sender IDs: {final_senders.count()}")
    print(f"   Approved Taarifa-SMS requests: {final_requests.count()}")
    print(f"   Total tenants: {tenants.count()}")
    
    # Check coverage
    tenants_with_senders = Tenant.objects.filter(sms_sender_ids__sender_id='Taarifa-SMS').distinct()
    coverage = (tenants_with_senders.count() / tenants.count()) * 100 if tenants.count() > 0 else 0
    
    print(f"   Tenant coverage: {tenants_with_senders.count()}/{tenants.count()} ({coverage:.1f}%)")
    
    if coverage >= 90:
        print("✅ Migration fix completed successfully!")
        return True
    else:
        print("⚠️  Some tenants may still need attention")
        return False

def test_api_endpoints():
    """Test API endpoints after fix."""
    print("\n🧪 Testing API Endpoints:")
    print("=" * 30)
    
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    client = Client()
    
    # Get a user with tenant (through memberships)
    user_with_tenant = User.objects.filter(memberships__isnull=False).first()
    if not user_with_tenant:
        print("❌ No users with tenants found")
        return False
    
    print(f"Testing with user: {user_with_tenant.email}")
    print(f"Tenant: {user_with_tenant.memberships.first().tenant.name if user_with_tenant.memberships.exists() else 'None'}")
    
    # Login user
    client.force_login(user_with_tenant)
    
    # Test endpoints
    endpoints = [
        ('/api/messaging/sender-ids/', 'Sender IDs List'),
        ('/api/messaging/sender-requests/available/', 'Available Sender IDs'),
        ('/api/messaging/sender-requests/default/overview/', 'Default Sender Overview'),
    ]
    
    success_count = 0
    
    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"✅ {name}: SUCCESS")
                    success_count += 1
                else:
                    print(f"❌ {name}: No data returned")
            else:
                print(f"❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    print(f"\nAPI Test Results: {success_count}/{len(endpoints)} passed")
    return success_count == len(endpoints)

if __name__ == "__main__":
    print("🚀 Live Server Sender ID Migration Fix")
    print("=" * 60)
    
    try:
        # Fix the migration issue
        migration_success = fix_sender_id_migration()
        
        # Test API endpoints
        api_success = test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("📊 Summary:")
        print(f"Migration Fix: {'✅ SUCCESS' if migration_success else '❌ FAILED'}")
        print(f"API Tests: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
        
        if migration_success and api_success:
            print("\n🎉 All fixes completed successfully!")
            print("\nNext steps:")
            print("1. Test your frontend to ensure sender IDs are loading")
            print("2. Check that 'Taarifa-SMS' appears in sender name dropdown")
            print("3. Verify no 'No approved sender names' errors")
        else:
            print("\n⚠️  Some issues remain. Check the output above.")
            
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
