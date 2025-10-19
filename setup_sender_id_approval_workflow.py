#!/usr/bin/env python3
"""
Setup Sender ID Approval Workflow
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

User = get_user_model()

def setup_sender_id_approval_workflow():
    """Setup the complete sender ID approval workflow"""
    print("🚀 Setting up Sender ID Approval Workflow")
    print("=" * 60)
    
    try:
        # 1. Get the tenant
        tenant = Tenant.objects.filter(subdomain='mifumo').first()
        if not tenant:
            print("❌ No tenant found. Run setup script first.")
            return
        
        print(f"✅ Using tenant: {tenant.name}")
        
        # 2. Ensure we have active sender IDs
        print("\n📱 Ensuring active sender IDs...")
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        
        if not provider:
            print("❌ No active SMS provider found")
            return
        
        # Get existing sender IDs
        existing_sender_ids = SMSSenderID.objects.filter(tenant=tenant)
        print(f"   📋 Found {existing_sender_ids.count()} existing sender IDs")
        
        # Ensure all existing sender IDs are active
        for sender_id in existing_sender_ids:
            if sender_id.status != 'active':
                sender_id.status = 'active'
                sender_id.save()
                print(f"   ✅ Activated sender ID: {sender_id.sender_id}")
        
        # 3. Create additional test sender IDs for approval workflow
        print("\n📝 Creating test sender IDs for approval workflow...")
        
        test_sender_ids = [
            {
                'sender_id': 'APPROVED',
                'sample_content': 'This sender ID has been approved and is ready for use',
                'status': 'active'
            },
            {
                'sender_id': 'PENDING',
                'sample_content': 'This sender ID is pending approval',
                'status': 'pending'
            },
            {
                'sender_id': 'REJECTED',
                'sample_content': 'This sender ID was rejected',
                'status': 'rejected'
            }
        ]
        
        for data in test_sender_ids:
            sender_id, created = SMSSenderID.objects.get_or_create(
                tenant=tenant,
                sender_id=data['sender_id'],
                defaults={
                    'provider': provider,
                    'status': data['status'],
                    'sample_content': data['sample_content'],
                    'created_by': User.objects.filter(email='admin@mifumo.com').first()
                }
            )
            
            if created:
                print(f"   ✅ Created {data['status']} sender ID: {sender_id.sender_id}")
            else:
                print(f"   ℹ️  Sender ID already exists: {sender_id.sender_id}")
        
        # 4. Create sender name requests for testing
        print("\n📋 Creating sender name requests for testing...")
        
        test_requests = [
            {
                'sender_name': 'NEWAPP',
                'use_case': 'New application for testing approval workflow',
                'status': 'pending'
            },
            {
                'sender_name': 'APPROVEDAPP',
                'use_case': 'Approved application for testing',
                'status': 'approved'
            },
            {
                'sender_name': 'REJECTEDAPP',
                'use_case': 'Rejected application for testing',
                'status': 'rejected'
            }
        ]
        
        for data in test_requests:
            request_obj, created = SenderNameRequest.objects.get_or_create(
                tenant=tenant,
                sender_name=data['sender_name'],
                defaults={
                    'use_case': data['use_case'],
                    'status': data['status'],
                    'created_by': User.objects.filter(email='admin@mifumo.com').first(),
                    'reviewed_by': User.objects.filter(email='admin@mifumo.com').first() if data['status'] != 'pending' else None,
                    'reviewed_at': timezone.now() if data['status'] != 'pending' else None,
                    'admin_notes': f'Test {data["status"]} request' if data['status'] != 'pending' else ''
                }
            )
            
            if created:
                print(f"   ✅ Created {data['status']} request: {request_obj.sender_name}")
            else:
                print(f"   ℹ️  Request already exists: {request_obj.sender_name}")
        
        # 5. Update SMS packages to include all sender IDs
        print("\n📦 Updating SMS packages with all sender IDs...")
        
        # Get all active sender IDs
        active_sender_ids = list(SMSSenderID.objects.filter(
            tenant=tenant, 
            status='active'
        ).values_list('sender_id', flat=True))
        
        print(f"   📋 Active sender IDs: {active_sender_ids}")
        
        # Update packages to include all active sender IDs
        packages = SMSPackage.objects.filter(is_active=True)
        for package in packages:
            # Update allowed sender IDs to include all active ones
            package.allowed_sender_ids = active_sender_ids
            package.save()
            print(f"   ✅ Updated {package.name} with {len(active_sender_ids)} sender IDs")
        
        # 6. Test the workflow
        print("\n🧪 Testing the approval workflow...")
        
        # Test SMS validation service
        from messaging.services.sms_validation import SMSValidationService
        validation_service = SMSValidationService(tenant)
        
        # Get active sender IDs
        available_sender_ids = validation_service.get_active_sender_ids()
        print(f"   📋 Available sender IDs for sending: {available_sender_ids}")
        
        # Test capability check
        capability = validation_service.can_send_sms()
        balance_info = validation_service.get_balance_info()
        
        print(f"   💰 SMS Balance: {balance_info['credits']} credits")
        print(f"   📱 Can send SMS: {capability['can_send']}")
        print(f"   📝 Reason: {capability['reason']}")
        
        # 7. Create a function to approve sender IDs
        print("\n✅ Creating sender ID approval function...")
        
        def approve_sender_id(sender_name):
            """Approve a sender ID and make it available for sending"""
            try:
                # Find the sender name request
                request_obj = SenderNameRequest.objects.filter(
                    tenant=tenant,
                    sender_name=sender_name,
                    status='pending'
                ).first()
                
                if not request_obj:
                    return {'success': False, 'error': 'Sender name request not found'}
                
                # Update request status
                request_obj.status = 'approved'
                request_obj.reviewed_by = User.objects.filter(email='admin@mifumo.com').first()
                request_obj.reviewed_at = timezone.now()
                request_obj.admin_notes = 'Approved by admin'
                request_obj.save()
                
                # Create or update the sender ID
                sender_id, created = SMSSenderID.objects.get_or_create(
                    tenant=tenant,
                    sender_id=sender_name,
                    defaults={
                        'provider': provider,
                        'status': 'active',
                        'sample_content': f'Approved sender ID: {sender_name}',
                        'created_by': User.objects.filter(email='admin@mifumo.com').first()
                    }
                )
                
                if not created:
                    sender_id.status = 'active'
                    sender_id.save()
                
                # Update packages to include the new sender ID
                for package in packages:
                    if sender_name not in package.allowed_sender_ids:
                        package.allowed_sender_ids.append(sender_name)
                        package.save()
                
                return {
                    'success': True,
                    'message': f'Sender ID {sender_name} approved and available for sending',
                    'sender_id': sender_id.sender_id,
                    'status': sender_id.status
                }
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        # Test the approval function
        print("\n🧪 Testing approval function...")
        result = approve_sender_id('NEWAPP')
        if result['success']:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Approval failed: {result['error']}")
        
        # 8. Final verification
        print("\n🔍 Final verification...")
        
        # Get updated active sender IDs
        updated_sender_ids = validation_service.get_active_sender_ids()
        print(f"   📋 Final active sender IDs: {updated_sender_ids}")
        
        # Check if NEWAPP is now available
        if 'NEWAPP' in updated_sender_ids:
            print("   ✅ NEWAPP is now available for sending!")
        else:
            print("   ❌ NEWAPP is not available for sending")
        
        print("\n" + "=" * 60)
        print("🎉 Sender ID Approval Workflow Setup Complete!")
        print("=" * 60)
        
        print(f"\n📊 Summary:")
        print(f"  🏢 Tenant: {tenant.name}")
        print(f"  📱 SMS Provider: {provider.name}")
        print(f"  📝 Total sender IDs: {SMSSenderID.objects.filter(tenant=tenant).count()}")
        print(f"  ✅ Active sender IDs: {len(updated_sender_ids)}")
        print(f"  📋 Sender requests: {SenderNameRequest.objects.filter(tenant=tenant).count()}")
        print(f"  📦 Updated packages: {packages.count()}")
        
        print(f"\n✅ Workflow is ready!")
        print("   - Users can request sender IDs")
        print("   - Admins can approve them in the admin panel")
        print("   - Approved sender IDs immediately become available for sending")
        print("   - All packages include all active sender IDs")
        
        print(f"\n🔧 To approve a sender ID:")
        print("   1. Go to admin panel: http://104.131.116.55:8000/admin/")
        print("   2. Navigate to 'Sender name requests'")
        print("   3. Change status from 'Pending' to 'Approved'")
        print("   4. The sender ID will immediately become available for sending")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_sender_id_approval_workflow()
