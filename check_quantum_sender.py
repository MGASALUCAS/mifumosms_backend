#!/usr/bin/env python
"""
Check for Quantum Sender ID specifically
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID, SMSProvider
from billing.models import SMSBalance
from tenants.models import Tenant

User = get_user_model()

print("QUANTUM SENDER ID CHECK")
print("="*50)

# Check all users and their sender IDs
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\nUser: {user.email}")
    if hasattr(user, 'tenant') and user.tenant:
        tenant = user.tenant
        print(f"  Tenant: {tenant.name}")
        
        # Check sender IDs for this tenant
        sender_ids = SMSSenderID.objects.filter(tenant=tenant)
        print(f"  Sender IDs: {sender_ids.count()}")
        
        for sender in sender_ids:
            print(f"    - {sender.sender_id} ({sender.status})")
            
        # Check for Quantum specifically
        quantum_senders = SMSSenderID.objects.filter(
            tenant=tenant,
            sender_id__icontains='quantum'
        )
        
        if quantum_senders.exists():
            print(f"  [FOUND] Quantum senders: {quantum_senders.count()}")
            for qs in quantum_senders:
                print(f"    - {qs.sender_id} ({qs.status})")
        else:
            print(f"  [NOT FOUND] No Quantum sender IDs")
            
        # Check SMS balance
        try:
            balance = SMSBalance.objects.get(tenant=tenant)
            print(f"  SMS Credits: {balance.credits}")
        except SMSBalance.DoesNotExist:
            print(f"  [NO BALANCE] No SMS balance found")
    else:
        print(f"  [NO TENANT] User has no tenant")

print(f"\n" + "="*50)
print("SEARCHING FOR QUANTUM IN ALL SENDER IDs")
print("="*50)

# Search for any sender ID containing "quantum" (case insensitive)
all_quantum = SMSSenderID.objects.filter(sender_id__icontains='quantum')
print(f"Total Quantum sender IDs found: {all_quantum.count()}")

for quantum in all_quantum:
    print(f"\nQuantum Sender ID: {quantum.sender_id}")
    print(f"  ID: {quantum.id}")
    print(f"  Status: {quantum.status}")
    print(f"  Tenant: {quantum.tenant.name}")
    print(f"  Provider: {quantum.provider.name if quantum.provider else 'None'}")
    print(f"  Created: {quantum.created_at}")

print(f"\n" + "="*50)
print("QUANTUM CHECK COMPLETE")
print("="*50)
