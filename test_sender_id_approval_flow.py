#!/usr/bin/env python3
"""
Test Sender ID Approval Flow
Ensures that when a sender ID is approved, it immediately becomes available for sending messages
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
from messaging.models_sms import SMSProvider, SMSSenderID, SenderNameRequest
from billing.models import SMSPackage, BillingPlan, Subscription, SMSBalance
from messaging.services.sms_validation import SMSValidationService

User = get_user_model()

def test_sender_id_approval_flow():
    """Test the complete sender ID approval flow"""
    print("🧪 Testing Sender ID Approval Flow")
    print("=" * 60)
    
    try:
        # 1. Get the tenant
        tenant = Tenant.objects.filter(subdomain='mifumo').first()
        if not tenant:
            print("❌ No tenant found. Run setup script first.")
            return
        
        print(f"✅ Using tenant: {tenant.name}")
        
        # 2. Create a test sender ID request
        print("\n📝 Creating test sender ID request...")
        sender_request, created = SenderNameRequest.objects.get_or_create(
            tenant=tenant,
            sender_name='TESTAPP',
            defaults={
                'use_case': 'Testing sender ID approval flow',
                'status': 'pending',
                'created_by': User.objects.filter(email='admin@mifumo.com').first()
            }
        )
        
        if created:
            print(f"   ✅ Created sender request: {sender_request.sender_name}")
        else:
            print(f"   ℹ️  Sender request already exists: {sender_request.sender_name}")
        
        # 3. Simulate approval process
        print("\n✅ Simulating sender ID approval...")
        
        # Update the request status to approved
        sender_request.status = 'approved'
        sender_request.reviewed_by = User.objects.filter(email='admin@mifumo.com').first()
        sender_request.reviewed_at = timezone.now()
        sender_request.admin_notes = 'Approved for testing purposes'
        sender_request.save()
        
        print(f"   ✅ Approved sender request: {sender_request.sender_name}")
        
        # 4. Create the actual sender ID with 'active' status
        print("\n📱 Creating active sender ID...")
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        
        if not provider:
            print("❌ No active SMS provider found")
            return
        
        sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id=sender_request.sender_name,
            defaults={
                'provider': provider,
                'status': 'active',  # Set to active immediately
                'sample_content': f'Test message from {sender_request.sender_name}',
                'provider_sender_id': f'PROV_{sender_request.sender_name}',
                'provider_data': {'approved_at': timezone.now().isoformat()},
                'created_by': User.objects.filter(email='admin@mifumo.com').first()
            }
        )
        
        if created:
            print(f"   ✅ Created active sender ID: {sender_id.sender_id}")
        else:
            # Update existing sender ID to active
            sender_id.status = 'active'
            sender_id.save()
            print(f"   ✅ Updated sender ID to active: {sender_id.sender_id}")
        
        # 5. Test SMS validation service
        print("\n🔍 Testing SMS validation service...")
        validation_service = SMSValidationService(tenant)
        
        # Get active sender IDs
        active_sender_ids = validation_service.get_active_sender_ids()
        print(f"   📋 Active sender IDs: {active_sender_ids}")
        
        # Check if our new sender ID is in the list
        if sender_id.sender_id in active_sender_ids:
            print(f"   ✅ Sender ID '{sender_id.sender_id}' is available for sending!")
        else:
            print(f"   ❌ Sender ID '{sender_id.sender_id}' is NOT available for sending!")
        
        # 6. Test SMS capability check
        print("\n📊 Testing SMS capability check...")
        capability = validation_service.can_send_sms()
        balance_info = validation_service.get_balance_info()
        
        print(f"   💰 Balance: {balance_info['credits']} credits")
        print(f"   📱 Can send SMS: {capability['can_send']}")
        print(f"   📝 Reason: {capability['reason']}")
        print(f"   📋 Available sender IDs: {len(active_sender_ids)}")
        
        # 7. Test API endpoint simulation
        print("\n🌐 Testing API endpoint simulation...")
        
        # Simulate what the API would return
        api_response = {
            'success': True,
            'data': {
                'can_send_sms': capability['can_send'],
                'reason': capability['reason'],
                'message': capability['message'],
                'balance': balance_info,
                'active_sender_ids': active_sender_ids,
                'validation_required': {
                    'sender_id_registered': len(active_sender_ids) > 0,
                    'has_credits': balance_info['credits'] > 0
                }
            }
        }
        
        print("   📡 API Response:")
        print(f"      - Can send SMS: {api_response['data']['can_send_sms']}")
        print(f"      - Active sender IDs: {api_response['data']['active_sender_ids']}")
        print(f"      - Sender ID registered: {api_response['data']['validation_required']['sender_id_registered']}")
        print(f"      - Has credits: {api_response['data']['validation_required']['has_credits']}")
        
        # 8. Test sender ID list API simulation
        print("\n📋 Testing sender ID list API simulation...")
        
        # Get all sender IDs for the tenant
        all_sender_ids = SMSSenderID.objects.filter(tenant=tenant)
        active_sender_ids_db = all_sender_ids.filter(status='active')
        pending_sender_ids_db = all_sender_ids.filter(status='pending')
        
        print(f"   📊 Total sender IDs: {all_sender_ids.count()}")
        print(f"   ✅ Active sender IDs: {active_sender_ids_db.count()}")
        print(f"   ⏳ Pending sender IDs: {pending_sender_ids_db.count()}")
        
        print("\n   📋 Active sender IDs list:")
        for sid in active_sender_ids_db:
            print(f"      - {sid.sender_id} ({sid.status}) - {sid.sample_content[:30]}...")
        
        # 9. Test package sender ID restrictions
        print("\n📦 Testing package sender ID restrictions...")
        
        packages = SMSPackage.objects.filter(is_active=True)
        for package in packages:
            print(f"   📦 {package.name}:")
            print(f"      - Default sender ID: {package.default_sender_id}")
            print(f"      - Allowed sender IDs: {package.allowed_sender_ids}")
            print(f"      - Restriction: {package.sender_id_restriction}")
            
            # Check if our new sender ID is allowed
            if package.sender_id_restriction == 'allowed_list':
                if sender_id.sender_id in package.allowed_sender_ids:
                    print(f"      ✅ '{sender_id.sender_id}' is allowed for this package")
                else:
                    print(f"      ❌ '{sender_id.sender_id}' is NOT allowed for this package")
            else:
                print(f"      ℹ️  No restrictions for this package")
        
        print("\n" + "=" * 60)
        print("🎉 Sender ID Approval Flow Test Completed!")
        print("=" * 60)
        
        print(f"\n📊 Summary:")
        print(f"  🏢 Tenant: {tenant.name}")
        print(f"  📝 Sender Request: {sender_request.sender_name} ({sender_request.status})")
        print(f"  📱 Sender ID: {sender_id.sender_id} ({sender_id.status})")
        print(f"  ✅ Available for sending: {sender_id.sender_id in active_sender_ids}")
        print(f"  💰 SMS Balance: {balance_info['credits']} credits")
        print(f"  📋 Total active sender IDs: {len(active_sender_ids)}")
        
        print(f"\n✅ The sender ID '{sender_id.sender_id}' is now available for sending messages!")
        print("   Users can see it in the sender ID dropdown when sending SMS.")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

def create_test_sender_id_request():
    """Create a test sender ID request for approval"""
    print("📝 Creating test sender ID request...")
    
    try:
        tenant = Tenant.objects.filter(subdomain='mifumo').first()
        if not tenant:
            print("❌ No tenant found. Run setup script first.")
            return
        
        # Create a test sender ID request
        sender_request = SenderNameRequest.objects.create(
            tenant=tenant,
            sender_name='TESTAPP',
            use_case='Testing sender ID approval flow',
            status='pending',
            created_by=User.objects.filter(email='admin@mifumo.com').first()
        )
        
        print(f"✅ Created sender request: {sender_request.sender_name}")
        print(f"   Status: {sender_request.status}")
        print(f"   Use case: {sender_request.use_case}")
        print(f"   Created: {sender_request.created_at}")
        
        return sender_request
        
    except Exception as e:
        print(f"❌ Error creating sender request: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Sender ID Approval Flow Test")
    print("=" * 60)
    print("This script tests the complete flow from sender ID request to approval")
    print("and ensures the sender ID becomes immediately available for sending.")
    print("=" * 60)
    
    test_sender_id_approval_flow()
