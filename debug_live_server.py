#!/usr/bin/env python3
"""
Live Server Debug Script - Sender ID API Issue
Run this on your live server to debug why frontend can't fetch sender IDs
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

def debug_sender_ids():
    """Debug sender ID issues on live server."""
    print("🔍 Debugging Sender ID API Issue on Live Server")
    print("=" * 60)
    
    # 1. Check all tenants
    print("\n1. Checking all tenants:")
    tenants = Tenant.objects.all()
    print(f"   Total tenants: {tenants.count()}")
    
    for tenant in tenants[:5]:  # Show first 5
        print(f"   - {tenant.name} (ID: {tenant.id})")
    
    # 2. Check all sender IDs
    print("\n2. Checking all sender IDs:")
    sender_ids = SMSSenderID.objects.all()
    print(f"   Total sender IDs: {sender_ids.count()}")
    
    for sender_id in sender_ids:
        print(f"   - {sender_id.sender_id} (Status: {sender_id.status}, Tenant: {sender_id.tenant.name})")
    
    # 3. Check sender ID requests
    print("\n3. Checking sender ID requests:")
    requests = SenderIDRequest.objects.all()
    print(f"   Total requests: {requests.count()}")
    
    for req in requests:
        print(f"   - {req.requested_sender_id} (Status: {req.status}, Tenant: {req.tenant.name})")
    
    # 4. Check specific tenant with sender ID
    print("\n4. Checking tenants with 'Taarifa-SMS':")
    taarifa_senders = SMSSenderID.objects.filter(sender_id='Taarifa-SMS')
    print(f"   Found {taarifa_senders.count()} 'Taarifa-SMS' sender IDs")
    
    for sender in taarifa_senders:
        print(f"   - Tenant: {sender.tenant.name}")
        print(f"     Status: {sender.status}")
        print(f"     Provider: {sender.provider.name if sender.provider else 'None'}")
        print(f"     Created: {sender.created_at}")
        
        # Check if tenant has users
        users = sender.tenant.memberships.all()
        print(f"     Users: {users.count()}")
        for membership in users[:3]:
            print(f"       - {membership.user.email} ({membership.role})")
    
    # 5. Test API logic
    print("\n5. Testing API logic:")
    for sender in taarifa_senders:
        tenant = sender.tenant
        print(f"\n   Testing tenant: {tenant.name}")
        
        # Test sender_ids_list logic
        active_senders = SMSSenderID.objects.filter(
            tenant=tenant,
            status='active'
        )
        print(f"   Active senders for API: {active_senders.count()}")
        for s in active_senders:
            print(f"     - {s.sender_id} ({s.status})")
        
        # Test available_sender_ids logic
        approved_requests = SenderIDRequest.objects.filter(
            tenant=tenant,
            status='approved'
        )
        print(f"   Approved requests: {approved_requests.count()}")
        
        active_sms_senders = SMSSenderID.objects.filter(
            tenant=tenant,
            status='active'
        )
        print(f"   Active SMS senders: {active_sms_senders.count()}")
    
    # 6. Check for common issues
    print("\n6. Checking for common issues:")
    
    # Issue 1: Sender IDs without tenants
    orphaned_senders = SMSSenderID.objects.filter(tenant__isnull=True)
    if orphaned_senders.exists():
        print(f"   ❌ Found {orphaned_senders.count()} sender IDs without tenants")
    
    # Issue 2: Sender IDs with inactive status
    inactive_senders = SMSSenderID.objects.filter(status='inactive')
    if inactive_senders.exists():
        print(f"   ⚠️  Found {inactive_senders.count()} inactive sender IDs")
    
    # Issue 3: Sender IDs without providers
    no_provider_senders = SMSSenderID.objects.filter(provider__isnull=True)
    if no_provider_senders.exists():
        print(f"   ⚠️  Found {no_provider_senders.count()} sender IDs without providers")
    
    # Issue 4: Tenants without sender IDs
    tenants_without_senders = Tenant.objects.exclude(sms_sender_ids__isnull=False)
    if tenants_without_senders.exists():
        print(f"   ❌ Found {tenants_without_senders.count()} tenants without sender IDs")
    
    print("\n" + "=" * 60)
    print("🔧 Debugging Complete!")
    
    # Recommendations
    print("\n📋 Recommendations:")
    print("1. Check if frontend is calling the correct API endpoint")
    print("2. Verify authentication is working")
    print("3. Check if user has a tenant")
    print("4. Verify sender ID status is 'active'")
    print("5. Check API response format")

def test_api_endpoints():
    """Test API endpoints directly."""
    print("\n🧪 Testing API Endpoints:")
    print("=" * 40)
    
    # Get a user with a tenant
    user_with_tenant = User.objects.filter(tenant__isnull=False).first()
    if not user_with_tenant:
        print("❌ No users with tenants found")
        return
    
    print(f"Testing with user: {user_with_tenant.email}")
    print(f"Tenant: {user_with_tenant.tenant.name}")
    
    # Test sender_ids_list logic
    tenant = user_with_tenant.tenant
    sender_ids = SMSSenderID.objects.filter(
        tenant=tenant,
        status='active'
    ).order_by('-created_at')
    
    print(f"\nSender IDs for API response:")
    api_data = []
    for sender_id in sender_ids:
        data = {
            'id': str(sender_id.id),
            'sender_id': sender_id.sender_id,
            'sample_content': sender_id.sample_content,
            'status': sender_id.status,
            'created_at': sender_id.created_at.isoformat(),
            'updated_at': sender_id.updated_at.isoformat()
        }
        api_data.append(data)
        print(f"  - {data}")
    
    print(f"\nAPI Response would be:")
    api_response = {
        'success': True,
        'data': api_data
    }
    print(f"  Success: {api_response['success']}")
    print(f"  Data count: {len(api_response['data'])}")

if __name__ == "__main__":
    try:
        debug_sender_ids()
        test_api_endpoints()
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
