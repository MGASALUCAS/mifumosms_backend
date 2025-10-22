"""
Quick Beem Africa Check - Run in Django Shell
Copy and paste this into: python manage.py shell
"""
from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID, SMSProvider
from billing.models import SMSBalance
from messaging.services.beem_sms import BeemSMSService
from django.conf import settings

User = get_user_model()

print("QUICK BEEM AFRICA CHECK")
print("="*50)

# Get user and tenant
user = User.objects.get(email='mgasa.loucat12@gmail.com')
tenant = user.tenant

print(f"User: {user.email}")
print(f"Tenant: {tenant.name}")

# 1. Check Sender IDs
print(f"\n1. SENDER IDs:")
sender_ids = SMSSenderID.objects.filter(tenant=tenant)
print(f"Total: {sender_ids.count()}")

for sender in sender_ids:
    status_icon = "✅" if sender.is_active else "❌"
    print(f"  {status_icon} {sender.sender_name} - {sender.status} (active: {sender.is_active})")

# 2. Check SMS Balance
print(f"\n2. SMS BALANCE:")
balance = SMSBalance.objects.get(tenant=tenant)
print(f"Credits: {balance.credits}")
print(f"Total Purchased: {balance.total_purchased}")
print(f"Total Used: {balance.total_used}")
print(f"Available: {balance.credits - balance.total_used}")

# 3. Check Beem API
print(f"\n3. BEEM API:")
api_key = getattr(settings, 'BEEM_API_KEY', None)
secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)

if api_key and secret_key:
    print(f"API Key: {api_key[:8]}...")
    print(f"Secret Key: {secret_key[:8]}...")
    
    # Test connection
    try:
        beem_service = BeemSMSService()
        result = beem_service.test_connection()
        if result.get('success'):
            print("✅ API Connection: SUCCESS")
        else:
            print(f"❌ API Connection: FAILED - {result.get('error')}")
    except Exception as e:
        print(f"❌ API Connection: ERROR - {str(e)}")
else:
    print("❌ Beem credentials not configured!")

# 4. Check Beem Balance
print(f"\n4. BEEM BALANCE:")
try:
    beem_service = BeemSMSService()
    balance_result = beem_service.get_balance()
    if balance_result.get('success'):
        data = balance_result.get('data', {})
        print(f"✅ Balance: {data.get('balance', 'N/A')} {data.get('currency', '')}")
    else:
        print(f"❌ Balance Check Failed: {balance_result.get('error')}")
except Exception as e:
    print(f"❌ Balance Check Error: {str(e)}")

print(f"\n" + "="*50)
print("QUICK CHECK COMPLETE")
print("="*50)
