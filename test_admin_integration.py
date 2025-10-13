#!/usr/bin/env python
"""
Test admin integration for sender name requests.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.admin import site
from messaging.models_sms import SenderNameRequest
from messaging.admin import SenderNameRequestAdmin

def test_admin_integration():
    """Test that the admin integration is working correctly."""
    print("🧪 Testing Admin Integration")
    print("=" * 40)

    # Test 1: Check if model is registered
    print("1. Checking model registration...")
    if SenderNameRequest in site._registry:
        print("✅ SenderNameRequest is registered in admin")
        admin_class = site._registry[SenderNameRequest]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ SenderNameRequest is NOT registered in admin")
        return

    # Test 2: Check admin configuration
    print("\n2. Checking admin configuration...")
    admin_instance = admin_class
    print(f"   List display: {admin_instance.list_display}")
    print(f"   List filter: {admin_instance.list_filter}")
    print(f"   Search fields: {admin_instance.search_fields}")
    print(f"   Actions: {admin_instance.actions}")

    # Test 3: Check database records
    print("\n3. Checking database records...")
    total_requests = SenderNameRequest.objects.count()
    print(f"   Total requests: {total_requests}")

    if total_requests > 0:
        # Show sample data
        sample_request = SenderNameRequest.objects.first()
        print(f"   Sample request: {sample_request.sender_name} ({sample_request.status})")
        print(f"   Created by: {sample_request.created_by}")
        print(f"   Tenant: {sample_request.tenant}")

    # Test 4: Check admin URLs
    print("\n4. Checking admin URLs...")
    try:
        from django.urls import reverse
        changelist_url = reverse('admin:messaging_sendernamerequest_changelist')
        print(f"   Changelist URL: {changelist_url}")

        if total_requests > 0:
            change_url = reverse('admin:messaging_sendernamerequest_change', args=[sample_request.pk])
            print(f"   Change URL: {change_url}")
    except Exception as e:
        print(f"   ❌ URL error: {str(e)}")

    # Test 5: Check custom methods
    print("\n5. Checking custom admin methods...")
    if hasattr(admin_instance, 'status_badge'):
        print("   ✅ status_badge method exists")
    else:
        print("   ❌ status_badge method missing")

    if hasattr(admin_instance, 'approve_requests'):
        print("   ✅ approve_requests action exists")
    else:
        print("   ❌ approve_requests action missing")

    if hasattr(admin_instance, 'reject_requests'):
        print("   ✅ reject_requests action exists")
    else:
        print("   ❌ reject_requests action missing")

    print("\n✅ Admin integration test completed!")

if __name__ == "__main__":
    test_admin_integration()
