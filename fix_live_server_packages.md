# Fix SMS Packages on Live Server

## Problem Identified

The live server (mifumosms.servehttp.com) has **incorrect SMS package data**:

**Current (WRONG):**
- Lite: 5,000 credits, 90,000 TZS, 18.00 TZS/unit
- Standard: 5,000 credits, 70,000 TZS, 14.00 TZS/unit ❌
- Pro: 5,000 credits, 60,000 TZS, 12.00 TZS/unit ❌

**Should Be (CORRECT from local server):**
- Lite: 5,000 credits, 90,000 TZS, 18.00 TZS/unit
- Standard: 50,000 credits, 700,000 TZS, 14.00 TZS/unit ✅
- Pro: 250,000 credits, 3,000,000 TZS, 12.00 TZS/unit ✅

---

## Solution: Update Packages on Live Server

### Option 1: Update Existing Packages (Recommended)

```bash
# SSH into live server
ssh user@your_live_server

# Navigate to project directory
cd /path/to/your/django/project

# Activate virtual environment
source venv/bin/activate

# Run the update command
python manage.py setup_sms_packages --update
```

This will **update** the existing packages with correct values:
- Lite: keeps same (already correct)
- Standard: updates from 5,000 → 50,000 credits
- Pro: updates from 5,000 → 250,000 credits

### Option 2: Reset and Recreate (Use with caution)

```bash
# This will DELETE all existing packages and create new ones
python manage.py setup_sms_packages --reset
```

⚠️ **Warning**: This will delete all existing packages and transactions!

---

## What the Command Does

The `setup_sms_packages` management command will:

1. **Lite Package** (Basic)
   - 5,000 credits
   - 90,000.00 TZS
   - 18.00 TZS per SMS
   - 40.0% savings
   - Features: Instant top-up, Basic delivery reports, Email receipt

2. **Standard Package** (Popular)
   - 50,000 credits ✅
   - 700,000.00 TZS ✅
   - 14.00 TZS per SMS
   - 53.3% savings
   - Features: Priority support, Advanced analytics, Campaign scheduling

3. **Pro Package** (Enterprise)
   - 250,000 credits ✅
   - 3,000,000.00 TZS ✅
   - 12.00 TZS per SMS
   - 60.0% savings
   - Features: Bulk campaign tools, API access, Custom sender IDs

---

## Verification Steps

After running the command, verify the changes:

1. **Check via Django shell:**
```bash
python manage.py shell -c "
from billing.models import SMSPackage
for p in SMSPackage.objects.all().order_by('price'):
    print(f'{p.name}: {p.credits:,} credits, {p.price:,.2f} TZS')
"
```

**Expected Output:**
```
Lite: 5,000 credits, 90,000.00 TZS
Standard: 50,000 credits, 700,000.00 TZS
Pro: 250,000 credits, 3,000,000.00 TZS
```

2. **Check via Admin Interface:**
   - Go to `https://mifumosms.servehttp.com/admin/billing/smspackage/`
   - Verify all packages have correct credits and prices

3. **Check via API (if available):**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://mifumosms.servehttp.com/api/billing/packages/"
```

---

## Why This Happened

The live server has **old database records** that were created before the correct package configurations were defined. The local server has the correct data because it was recently set up with the proper configuration.

---

## Next Steps

1. ✅ SSH into live server
2. ✅ Run `python manage.py setup_sms_packages --update`
3. ✅ Verify packages are correct
4. ✅ Restart the web server (if needed)
5. ✅ Test the packages in the admin interface

---

## Rollback (if needed)

If something goes wrong, you can restore the original values:

```python
# In Django shell
from billing.models import SMSPackage
from decimal import Decimal

# Restore Lite (already correct)
lite = SMSPackage.objects.get(name='Lite')
lite.credits = 5000
lite.price = Decimal('90000.00')
lite.save()

# Restore Standard to wrong value
std = SMSPackage.objects.get(name='Standard')
std.credits = 5000
std.price = Decimal('70000.00')
std.save()

# Restore Pro to wrong value
pro = SMSPackage.objects.get(name='Pro')
pro.credits = 5000
pro.price = Decimal('60000.00')
pro.save()
```

But you probably **don't want to do this** - the correct values are much better! ✅
