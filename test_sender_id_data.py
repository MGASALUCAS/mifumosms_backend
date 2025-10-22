#!/usr/bin/env python3
"""
Test sender ID functionality by checking database directly
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

def test_sender_id_data():
    print("🧪 Testing Sender ID Data in Database")
    print("=" * 50)
    
    # Check tenants
    tenants = Tenant.objects.all()
    print(f"📊 Total tenants: {tenants.count()}")
    
    # Check Taarifa-SMS sender IDs
    taarifa_senders = SMSSenderID.objects.filter(sender_id='Taarifa-SMS')
    print(f"📊 Taarifa-SMS sender IDs: {taarifa_senders.count()}")
    
    # Check Taarifa-SMS requests
    taarifa_requests = SenderIDRequest.objects.filter(requested_sender_id='Taarifa-SMS')
    print(f"📊 Taarifa-SMS requests: {taarifa_requests.count()}")
    
    # Check active sender IDs
    active_senders = SMSSenderID.objects.filter(status='active')
    print(f"📊 Active sender IDs: {active_senders.count()}")
    
    # Check approved requests
    approved_requests = SenderIDRequest.objects.filter(status='approved')
    print(f"📊 Approved requests: {approved_requests.count()}")
    
    # Show some examples
    print(f"\n📝 Sample Taarifa-SMS sender IDs:")
    for sender in taarifa_senders[:3]:
        print(f"   - {sender.sender_id} (Status: {sender.status}, Tenant: {sender.tenant.name})")
    
    print(f"\n📝 Sample Taarifa-SMS requests:")
    for request in taarifa_requests[:3]:
        print(f"   - {request.requested_sender_id} (Status: {request.status}, Tenant: {request.tenant.name})")
    
    # Test user with tenant
    user = User.objects.filter(memberships__isnull=False).first()
    if user:
        tenant = user.memberships.first().tenant
        print(f"\n👤 Test user: {user.email}")
        print(f"🏢 Tenant: {tenant.name}")
        
        # Check if user's tenant has Taarifa-SMS
        tenant_sender = SMSSenderID.objects.filter(
            tenant=tenant,
            sender_id='Taarifa-SMS'
        ).first()
        
        if tenant_sender:
            print(f"✅ Tenant has Taarifa-SMS sender ID (Status: {tenant_sender.status})")
        else:
            print(f"❌ Tenant missing Taarifa-SMS sender ID")
        
        # Check if user's tenant has approved request
        tenant_request = SenderIDRequest.objects.filter(
            tenant=tenant,
            requested_sender_id='Taarifa-SMS',
            status='approved'
        ).first()
        
        if tenant_request:
            print(f"✅ Tenant has approved Taarifa-SMS request")
        else:
            print(f"❌ Tenant missing approved Taarifa-SMS request")
    
    # Calculate coverage
    coverage = (taarifa_senders.count() / tenants.count()) * 100 if tenants.count() > 0 else 0
    print(f"\n📊 Coverage: {taarifa_senders.count()}/{tenants.count()} ({coverage:.1f}%)")
    
    return taarifa_senders.count() > 0 and taarifa_requests.count() > 0

if __name__ == "__main__":
    success = test_sender_id_data()
    if success:
        print("\n🎉 Sender ID data is properly set up!")
    else:
        print("\n⚠️  Sender ID data needs attention.")
