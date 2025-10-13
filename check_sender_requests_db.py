#!/usr/bin/env python
"""
Script to check sender name requests in the database and verify admin access.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from messaging.models_sms import SenderNameRequest

User = get_user_model()

def check_database():
    """Check the database for sender name requests and user/tenant relationships."""
    print("🔍 Checking Sender Name Requests Database")
    print("=" * 50)

    # Check users
    print("\n1. Users in database:")
    users = User.objects.all()
    for user in users:
        print(f"   - User {user.id}: {user.email} (Staff: {user.is_staff})")
        # Check user's tenant
        tenant = getattr(user, 'tenant', None)
        if tenant:
            print(f"     Tenant: {tenant.name} ({tenant.id})")
        else:
            print(f"     Tenant: None")

    # Check tenants
    print("\n2. Tenants in database:")
    tenants = Tenant.objects.all()
    for tenant in tenants:
        print(f"   - Tenant {tenant.id}: {tenant.name} (Active: {tenant.is_active})")

    # Check memberships
    print("\n3. User-Tenant Memberships:")
    memberships = Membership.objects.all()
    for membership in memberships:
        print(f"   - User {membership.user.email} -> Tenant {membership.tenant.name} (Status: {membership.status})")

    # Check sender name requests
    print("\n4. Sender Name Requests:")
    requests = SenderNameRequest.objects.all()
    if requests.exists():
        for req in requests:
            print(f"   - Request {req.id}: {req.sender_name} (Status: {req.status})")
            print(f"     Tenant: {req.tenant.name if req.tenant else 'None'}")
            print(f"     Created by: {req.created_by.email if req.created_by else 'None'}")
            print(f"     Created at: {req.created_at}")
    else:
        print("   No sender name requests found in database")

    # Test admin access
    print("\n5. Testing Admin Access:")
    admin_users = User.objects.filter(is_staff=True)
    for admin in admin_users:
        print(f"\n   Testing admin: {admin.email}")

        # Simulate request with tenant
        tenant = getattr(admin, 'tenant', None)
        if tenant:
            print(f"     Admin has tenant: {tenant.name}")

            # Check if admin can see all requests for their tenant
            admin_requests = SenderNameRequest.objects.filter(tenant=tenant)
            print(f"     Admin can see {admin_requests.count()} requests for their tenant")

            # Check if admin can see their own requests
            own_requests = SenderNameRequest.objects.filter(tenant=tenant, created_by=admin)
            print(f"     Admin has {own_requests.count()} own requests")
        else:
            print(f"     Admin has NO tenant - this is the problem!")

    print("\n✅ Database check completed!")

def create_test_data():
    """Create test sender name requests for testing."""
    print("\n🧪 Creating Test Data")
    print("=" * 30)

    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Please create a tenant first.")
        return

    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No user found. Please create a user first.")
        return

    # Create test sender name requests
    test_requests = [
        {
            'sender_name': 'TESTCOMPANY',
            'use_case': 'This is a test sender name request for testing purposes.',
            'status': 'pending'
        },
        {
            'sender_name': 'ADMINCORP',
            'use_case': 'This is an admin test sender name request.',
            'status': 'approved'
        },
        {
            'sender_name': 'REJECTED123',
            'use_case': 'This is a rejected test sender name request.',
            'status': 'rejected'
        }
    ]

    for req_data in test_requests:
        request, created = SenderNameRequest.objects.get_or_create(
            tenant=tenant,
            sender_name=req_data['sender_name'],
            defaults={
                'use_case': req_data['use_case'],
                'status': req_data['status'],
                'created_by': user
            }
        )

        if created:
            print(f"✅ Created test request: {req_data['sender_name']}")
        else:
            print(f"ℹ️  Test request already exists: {req_data['sender_name']}")

    print(f"\n📊 Total sender name requests: {SenderNameRequest.objects.count()}")

if __name__ == "__main__":
    check_database()
    create_test_data()
    check_database()
