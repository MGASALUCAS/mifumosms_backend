# Live Server Migration Fix - Quick Commands

## 🚨 **Migration Failed - Here's How to Fix It**

The migration failed because some tenants already have sender ID requests for "Taarifa-SMS", causing a UNIQUE constraint violation.

## 🔧 **Quick Fix Commands**

### **Option 1: Run the Fix Script**
```bash
# On your live server:
python fix_migration_live_server.py
```

This script will:
- ✅ Check current state
- ✅ Create missing sender IDs
- ✅ Create missing sender ID requests
- ✅ Test API endpoints
- ✅ Show coverage statistics

### **Option 2: Manual Fix Commands**

```bash
# 1. Mark the migration as fake (skip it)
python manage.py migrate accounts 0003_add_default_sender_ids --fake

# 2. Run the fix script
python fix_migration_live_server.py

# 3. Verify everything is working
python manage.py shell -c "
from messaging.models_sms import SMSSenderID
from messaging.models_sender_requests import SenderIDRequest
print(f'Sender IDs: {SMSSenderID.objects.filter(sender_id=\"Taarifa-SMS\").count()}')
print(f'Requests: {SenderIDRequest.objects.filter(requested_sender_id=\"Taarifa-SMS\").count()}')
"
```

### **Option 3: Database Direct Fix**

```bash
# If you prefer to fix directly in the database:
python manage.py shell -c "
from messaging.models_sms import SMSSenderID, SMSProvider
from messaging.models_sender_requests import SenderIDRequest
from tenants.models import Tenant

# Create missing sender IDs
for tenant in Tenant.objects.all():
    if not SMSSenderID.objects.filter(tenant=tenant, sender_id='Taarifa-SMS').exists():
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        if provider:
            SMSSenderID.objects.create(
                tenant=tenant,
                sender_id='Taarifa-SMS',
                provider=provider,
                status='active',
                sample_content='A test use case for the sender name purposely used for information transfer.',
                created_by=provider.created_by
            )
            print(f'Created sender ID for {tenant.name}')

print('Fix completed!')
"
```

## 🎯 **What the Fix Does**

1. **Checks Current State**: Shows how many tenants have sender IDs
2. **Creates Missing Sender IDs**: Adds "Taarifa-SMS" for tenants that don't have it
3. **Creates Missing Requests**: Adds sender ID requests for tracking
4. **Tests API Endpoints**: Verifies the APIs are working
5. **Shows Coverage**: Displays how many tenants are covered

## ✅ **Expected Results**

After running the fix:
- ✅ All tenants have "Taarifa-SMS" sender ID
- ✅ All tenants have approved sender ID requests
- ✅ API endpoints return sender IDs correctly
- ✅ Frontend can fetch sender IDs
- ✅ No more "No approved sender names" error

## 🚀 **Run This Now**

```bash
# On your live server, run:
python fix_migration_live_server.py
```

This will fix the migration issue and ensure all users have access to the default sender ID "Taarifa-SMS".
