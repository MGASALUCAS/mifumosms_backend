"""
Check Beem Africa Sender IDs and Credits
This script checks both local database and Beem Africa API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID, SMSProvider
from billing.models import SMSBalance
from messaging.services.beem_sms import BeemSMSService
import requests
from django.conf import settings

User = get_user_model()

print("BEEM AFRICA SENDER IDS & CREDITS CHECK")
print("="*60)

# Get the user and tenant
try:
    user = User.objects.get(email='mgasa.loucat12@gmail.com')
    tenant = user.tenant
    
    print(f"✅ User: {user.email}")
    print(f"✅ Tenant: {tenant.name}")
    print(f"✅ Tenant ID: {tenant.id}")
    
except User.DoesNotExist:
    print("❌ User not found! Available users:")
    for u in User.objects.all()[:5]:
        print(f"   - {u.email}")
    exit()

# 1. Check Local Database Sender IDs
print(f"\n1. LOCAL DATABASE SENDER IDs")
print("-" * 40)

sender_ids = SMSSenderID.objects.filter(tenant=tenant)
print(f"Total Sender IDs in DB: {sender_ids.count()}")

for sender in sender_ids:
    print(f"\n📱 Sender ID: {sender.sender_name}")
    print(f"   ID: {sender.id}")
    print(f"   Status: {sender.status}")
    print(f"   Active: {sender.is_active}")
    print(f"   Provider: {sender.provider.name if sender.provider else 'None'}")
    print(f"   Created: {sender.created_at}")
    print(f"   Updated: {sender.updated_at}")

# 2. Check SMS Balance
print(f"\n2. SMS BALANCE")
print("-" * 40)

try:
    balance = SMSBalance.objects.get(tenant=tenant)
    print(f"✅ SMS Balance Found:")
    print(f"   Credits: {balance.credits}")
    print(f"   Total Purchased: {balance.total_purchased}")
    print(f"   Total Used: {balance.total_used}")
    print(f"   Available: {balance.credits - balance.total_used}")
    print(f"   Last Updated: {balance.updated_at}")
except SMSBalance.DoesNotExist:
    print("❌ No SMS Balance found!")

# 3. Check Beem Africa API
print(f"\n3. BEEM AFRICA API CHECK")
print("-" * 40)

# Get Beem provider
beem_provider = SMSProvider.objects.filter(
    tenant=tenant,
    provider_type='beem'
).first()

if not beem_provider:
    print("❌ No Beem provider found in database!")
    print("   Creating default Beem provider...")
    
    beem_provider = SMSProvider.objects.create(
        tenant=tenant,
        name='Default Beem Provider',
        provider_type='beem',
        is_default=True,
        is_active=True
    )
    print(f"✅ Created Beem provider: {beem_provider.id}")

print(f"✅ Beem Provider: {beem_provider.name}")
print(f"   ID: {beem_provider.id}")
print(f"   Active: {beem_provider.is_active}")

# Check Beem API credentials
api_key = getattr(settings, 'BEEM_API_KEY', None)
secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)

if not api_key or not secret_key:
    print("❌ Beem API credentials not configured!")
    print("   Please check BEEM_API_KEY and BEEM_SECRET_KEY in settings")
else:
    print(f"✅ Beem API Key: {api_key[:8]}...")
    print(f"✅ Beem Secret Key: {secret_key[:8]}...")

# 4. Test Beem API Connection
print(f"\n4. BEEM API CONNECTION TEST")
print("-" * 40)

try:
    # Initialize Beem service
    beem_service = BeemSMSService()
    
    # Test connection
    print("Testing Beem API connection...")
    connection_result = beem_service.test_connection()
    
    if connection_result.get('success'):
        print("✅ Beem API connection successful!")
        print(f"   Response: {connection_result.get('message', 'Connected')}")
    else:
        print("❌ Beem API connection failed!")
        print(f"   Error: {connection_result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Error testing Beem connection: {str(e)}")

# 5. Check Beem Balance
print(f"\n5. BEEM ACCOUNT BALANCE")
print("-" * 40)

try:
    balance_result = beem_service.get_balance()
    
    if balance_result.get('success'):
        print("✅ Beem balance retrieved successfully!")
        balance_data = balance_result.get('data', {})
        print(f"   Balance: {balance_data.get('balance', 'N/A')}")
        print(f"   Currency: {balance_data.get('currency', 'N/A')}")
        print(f"   Status: {balance_data.get('status', 'N/A')}")
    else:
        print("❌ Failed to get Beem balance!")
        print(f"   Error: {balance_result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Error getting Beem balance: {str(e)}")

# 6. Check Beem Sender IDs
print(f"\n6. BEEM SENDER IDs (if available)")
print("-" * 40)

try:
    # Note: Beem API might not have a direct endpoint to list sender IDs
    # This would depend on Beem's API documentation
    print("Note: Beem API may not provide sender ID listing endpoint")
    print("Sender IDs are typically managed through their dashboard")
    print("Check: https://dashboard.beem.africa/")
    
except Exception as e:
    print(f"❌ Error checking Beem sender IDs: {str(e)}")

# 7. Summary
print(f"\n7. SUMMARY")
print("-" * 40)

print(f"📊 Local Database:")
print(f"   Sender IDs: {sender_ids.count()}")
print(f"   Active Sender IDs: {sender_ids.filter(is_active=True).count()}")
print(f"   SMS Credits: {balance.credits if 'balance' in locals() else 'N/A'}")

print(f"\n📊 Beem Africa:")
print(f"   API Connected: {'Yes' if 'connection_result' in locals() and connection_result.get('success') else 'No'}")
print(f"   Balance Retrieved: {'Yes' if 'balance_result' in locals() and balance_result.get('success') else 'No'}")

print(f"\n" + "="*60)
print("CHECK COMPLETE")
print("="*60)

print(f"\nNext Steps:")
print(f"1. If sender IDs are missing, create them in Beem dashboard")
print(f"2. If credits are low, top up through Beem dashboard")
print(f"3. If API connection fails, check credentials in settings")
print(f"4. Sync sender IDs from Beem to local database if needed")
