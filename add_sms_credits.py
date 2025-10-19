#!/usr/bin/env python
"""
Script to add SMS credits to admin users
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from billing.models import SMSBalance, SMSPackage
# from billing.services.stripe_service import StripeService
import logging

User = get_user_model()

def add_credits_to_admin():
    """Add SMS credits to admin users"""
    
    # Get all admin users
    admin_users = User.objects.filter(is_staff=True)
    
    for admin_user in admin_users:
        tenant = admin_user.tenant
        if not tenant:
            print(f"Admin user {admin_user.email} has no tenant, skipping...")
            continue
            
        print(f"Processing admin user: {admin_user.email}")
        print(f"Tenant: {tenant.name}")
        
        # Get or create SMS balance
        sms_balance, created = SMSBalance.objects.get_or_create(
            tenant=tenant,
            defaults={
                'credits': 1000,  # Give admin users 1000 free credits
                'total_purchased': 1000
            }
        )
        
        if created:
            print(f"Created new SMS balance with 1000 credits")
        else:
            # Add more credits to existing balance
            sms_balance.credits += 1000
            sms_balance.total_purchased += 1000
            sms_balance.save()
            print(f"Added 1000 credits. New balance: {sms_balance.credits}")
        
        # Create a free SMS package for admin users
        package, created = SMSPackage.objects.get_or_create(
            name="Admin Free Package",
            defaults={
                'credits': 1000,
                'price': 0.0,
                'unit_price': 0.0,
                'is_active': True,
                'package_type': 'admin_free'
            }
        )
        
        if created:
            print(f"Created free admin package")
        else:
            print(f"Admin package already exists")

if __name__ == "__main__":
    add_credits_to_admin()
