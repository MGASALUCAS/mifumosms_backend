# SMS Sending 400 Error - Diagnostic & Fix Guide

## Problem
The frontend is getting a **400 Bad Request** error when trying to send SMS messages with sender ID "Quantum".

**Error Details:**
```
POST https://mifumosms.servehttp.com/api/messaging/sms/send/ 400 (Bad Request)
Data: {message: 'Hello Magesa welcome message from Quantum Intelligence', recipients: ['255614853618'], sender_id: 'Quantum'}
```

## Root Cause Analysis

Based on code review, the most likely causes are:

1. **Sender ID "Quantum" doesn't exist** - The sender ID needs to be created and approved
2. **Sender ID exists but is inactive** - Status needs to be 'active'
3. **No SMS credits available** - User needs credits to send SMS

## Diagnostic Steps

### Step 1: Run Diagnostic Script

On the **SERVER**, run:

```bash
cd /srv/mifumosms_backend
python test_sms_issue.py
```

This will check:
- SMS Balance and credits
- Sender ID status
- Validation errors

### Step 2: Check Django Shell

If the script shows issues, check manually:

```bash
python manage.py shell
```

Then run:

```python
from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID
from billing.models import SMSBalance

User = get_user_model()

# Get the user
user = User.objects.get(email='mgasa.loucat12@gmail.com')
tenant = user.tenant

# Check SMS Balance
balance = SMSBalance.objects.get(tenant=tenant)
print(f"SMS Credits: {balance.credits}")
print(f"Total Purchased: {balance.total_purchased}")
print(f"Total Used: {balance.total_used}")

# Check Sender IDs
sender_ids = SMSSenderID.objects.filter(tenant=tenant)
print(f"\nSender IDs ({sender_ids.count()}):")
for sender in sender_ids:
    print(f"  - {sender.sender_name}: {sender.status} (active: {sender.is_active})")

# Check for Quantum specifically
quantum = SMSSenderID.objects.filter(tenant=tenant, sender_name__iexact='Quantum').first()
if quantum:
    print(f"\nQuantum Sender ID:")
    print(f"  Status: {quantum.status}")
    print(f"  Active: {quantum.is_active}")
else:
    print(f"\n❌ Quantum sender ID NOT found!")
```

## Fixes

### Fix 1: Create/Activate Quantum Sender ID

If the sender ID doesn't exist or is inactive:

```python
from messaging.models_sms import SMSSenderID, SMSProvider
from django.contrib.auth import get_user_model

User = get_user_model()

# Get the user and tenant
user = User.objects.get(email='mgasa.loucat12@gmail.com')
tenant = user.tenant

# Get or create Beem provider
provider = SMSProvider.objects.filter(tenant=tenant, provider_type='beem').first()
if not provider:
    provider = SMSProvider.objects.create(
        tenant=tenant,
        name='Default Beem Provider',
        provider_type='beem',
        is_default=True,
        is_active=True
    )
    print(f"✅ Created Beem provider: {provider.id}")

# Create or update Quantum sender ID
quantum, created = SMSSenderID.objects.update_or_create(
    tenant=tenant,
    sender_name='QUANTUM',  # Uppercase for consistency
    defaults={
        'provider': provider,
        'status': 'active',
        'is_active': True,
        'is_default': False
    }
)

if created:
    print(f"✅ Created Quantum sender ID: {quantum.id}")
else:
    print(f"✅ Updated Quantum sender ID: {quantum.id}")

print(f"   Status: {quantum.status}")
print(f"   Active: {quantum.is_active}")
```

### Fix 2: Ensure SMS Credits

If the SMS balance is zero:

```python
from billing.models import SMSBalance

# Get the balance
balance = SMSBalance.objects.get(tenant=tenant)

# Add credits if needed
if balance.credits == 0:
    balance.credits = 100
    balance.total_purchased = 100
    balance.save()
    print(f"✅ Added 100 credits to SMS balance")

print(f"Final balance: {balance.credits} credits")
```

### Fix 3: Update total_purchased if needed

If `total_purchased` is 0 but `credits` is 100:

```python
from billing.models import SMSBalance

balance = SMSBalance.objects.get(tenant=tenant)
if balance.total_purchased == 0 and balance.credits > 0:
    balance.total_purchased = balance.credits
    balance.save()
    print(f"✅ Fixed total_purchased: {balance.total_purchased}")
```

## Complete Fix Script

Run this in Django shell to fix everything:

```python
from django.contrib.auth import get_user_model
from messaging.models_sms import SMSSenderID, SMSProvider
from billing.models import SMSBalance

User = get_user_model()

print("FIXING SMS SENDING ISSUE")
print("="*60)

# Get the user and tenant
user = User.objects.get(email='mgasa.loucat12@gmail.com')
tenant = user.tenant

print(f"User: {user.email}")
print(f"Tenant: {tenant.name}")

# 1. Fix SMS Balance
balance, _ = SMSBalance.objects.get_or_create(tenant=tenant, defaults={'credits': 0})
if balance.credits == 0:
    balance.credits = 100
if balance.total_purchased == 0 and balance.credits > 0:
    balance.total_purchased = balance.credits
balance.save()

print(f"\n✅ SMS Balance Fixed:")
print(f"   Credits: {balance.credits}")
print(f"   Total Purchased: {balance.total_purchased}")

# 2. Fix Sender ID
provider, _ = SMSProvider.objects.get_or_create(
    tenant=tenant,
    provider_type='beem',
    defaults={
        'name': 'Default Beem Provider',
        'is_default': True,
        'is_active': True
    }
)

quantum, created = SMSSenderID.objects.update_or_create(
    tenant=tenant,
    sender_name='QUANTUM',
    defaults={
        'provider': provider,
        'status': 'active',
        'is_active': True,
        'is_default': False
    }
)

print(f"\n✅ Quantum Sender ID Fixed:")
print(f"   ID: {quantum.id}")
print(f"   Status: {quantum.status}")
print(f"   Active: {quantum.is_active}")
print(f"   Created: {created}")

# 3. Verify the fix
from messaging.services.sms_validation import SMSValidationService

validation_service = SMSValidationService(tenant)
validation_result = validation_service.validate_sms_sending(
    sender_id='QUANTUM',
    required_credits=1
)

print(f"\n✅ Validation Check:")
print(f"   Valid: {validation_result['valid']}")
if validation_result['valid']:
    print(f"   Available Credits: {validation_result['available_credits']}")
    print(f"   ✅ SMS sending should now work!")
else:
    print(f"   ❌ Error: {validation_result['error']}")

print(f"\n" + "="*60)
print("FIX COMPLETE")
print("="*60)
```

## Testing

After applying the fixes, test SMS sending:

1. **From Frontend**: Try sending an SMS again
2. **From API**: Use curl or Postman:

```bash
curl -X POST https://mifumosms.servehttp.com/api/messaging/sms/send/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message from Quantum",
    "recipients": ["255614853618"],
    "sender_id": "QUANTUM"
  }'
```

## Expected Success Response

```json
{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "uuid",
    "provider": "beem",
    "recipient_count": 1,
    "cost_estimate": 0.10,
    "status": "queued"
  }
}
```

## Common Errors & Solutions

### Error: "Sender name is missing or not available"
**Solution**: Run Fix 1 to create/activate the sender ID

### Error: "Insufficient SMS balance"
**Solution**: Run Fix 2 to add credits

### Error: "You are not linked to any organization"
**Solution**: User needs to be assigned to a tenant

### Error: "Invalid phone numbers"
**Solution**: Ensure phone numbers are in international format (255...)

## Notes

- Sender IDs are typically stored in UPPERCASE (e.g., "QUANTUM")
- The frontend can send "Quantum" (any case), the backend will handle it
- SMS credits are deducted when the message is queued
- Check server logs for detailed error messages: `tail -f /var/log/mifumosms/gunicorn-error.log`

## Need Help?

If the issue persists:
1. Check server logs for detailed errors
2. Run the diagnostic script again
3. Verify the user is logged in with correct credentials
4. Check if the sender ID has any special restrictions

