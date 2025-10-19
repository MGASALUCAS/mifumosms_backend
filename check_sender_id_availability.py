#!/usr/bin/env python3
"""
Check Sender ID Availability
Quick script to check what sender IDs are available for sending messages
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSSenderID
from messaging.services.sms_validation import SMSValidationService

def check_sender_id_availability():
    """Check what sender IDs are available for sending"""
    print("🔍 Checking Sender ID Availability")
    print("=" * 50)
    
    try:
        # Get the tenant
        tenant = Tenant.objects.filter(subdomain='mifumo').first()
        if not tenant:
            print("❌ No tenant found. Run setup script first.")
            return
        
        print(f"🏢 Tenant: {tenant.name}")
        
        # Get all sender IDs
        all_sender_ids = SMSSenderID.objects.filter(tenant=tenant)
        print(f"\n📊 Total Sender IDs: {all_sender_ids.count()}")
        
        # Group by status
        status_counts = {}
        for sender_id in all_sender_ids:
            status = sender_id.status
            if status not in status_counts:
                status_counts[status] = []
            status_counts[status].append(sender_id.sender_id)
        
        for status, sender_ids in status_counts.items():
            print(f"\n📋 {status.upper()} ({len(sender_ids)}):")
            for sid in sender_ids:
                print(f"   - {sid}")
        
        # Check what's available for sending
        print(f"\n🔍 Available for Sending:")
        validation_service = SMSValidationService(tenant)
        active_sender_ids = validation_service.get_active_sender_ids()
        
        if active_sender_ids:
            print(f"   ✅ {len(active_sender_ids)} sender IDs available:")
            for sid in active_sender_ids:
                print(f"      - {sid}")
        else:
            print("   ❌ No sender IDs available for sending")
        
        # Check SMS capability
        print(f"\n📱 SMS Capability:")
        capability = validation_service.can_send_sms()
        balance_info = validation_service.get_balance_info()
        
        print(f"   💰 Balance: {balance_info['credits']} credits")
        print(f"   📱 Can send SMS: {capability['can_send']}")
        print(f"   📝 Reason: {capability['reason']}")
        
        # Check packages
        from billing.models import SMSPackage
        packages = SMSPackage.objects.filter(is_active=True)
        print(f"\n📦 SMS Packages ({packages.count()}):")
        
        for package in packages:
            print(f"   📦 {package.name}:")
            print(f"      - Default: {package.default_sender_id}")
            print(f"      - Allowed: {package.allowed_sender_ids}")
            print(f"      - Restriction: {package.sender_id_restriction}")
        
        print(f"\n✅ Summary:")
        print(f"   - Total sender IDs: {all_sender_ids.count()}")
        print(f"   - Active for sending: {len(active_sender_ids)}")
        print(f"   - Can send SMS: {capability['can_send']}")
        print(f"   - Available packages: {packages.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sender_id_availability()
