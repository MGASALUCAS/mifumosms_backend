# Live Server Deployment Instructions

## What to Run on Live Server

### Step 1: Pull Latest Code
```bash
# SSH into live server
ssh user@your_server_ip

# Navigate to project
cd /path/to/mifumosms_backend

# Pull latest code
git pull origin backend_testing
```

### Step 2: Install Dependencies (if any)
```bash
# Activate virtual environment
source venv/bin/activate

# Install any new dependencies (if needed)
pip install -r requirements.txt
```

### Step 3: Restart Server
```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For Apache
sudo service apache2 restart

# Or your specific setup
```

### Step 4: Update SMS Packages (Fix incorrect data)
```bash
# Run the update command to fix package credits
python manage.py setup_sms_packages --update
```

**This will update:**
- Lite: 5,000 credits ✅ (already correct)
- Standard: 5,000 → **50,000 credits** 🔄
- Pro: 5,000 → **250,000 credits** 🔄

### Step 5: Verify Changes
```bash
# Check packages via Django shell
python manage.py shell -c "
from billing.models import SMSPackage
for p in SMSPackage.objects.all().order_by('price'):
    print(f'{p.name}: {p.credits:,} credits, {p.price:,.2f} TZS, Subtitle: {p.subtitle}')
"
```

**Expected Output:**
```
Lite: 5,000 credits, 90,000.00 TZS, Subtitle: 5,000 SMS Credits
Standard: 50,000 credits, 700,000.00 TZS, Subtitle: 50,000 SMS Credits
Pro: 250,000 credits, 3,000,000.00 TZS, Subtitle: 250,000 SMS Credits
```

## API Testing

Test the API to see the new `subtitle` field:

```bash
# Get all packages
curl "https://mifumosms.servehttp.com/api/billing/packages/"

# Or via browser
# https://mifumosms.servehttp.com/api/billing/packages/
```

## Verification Checklist

✅ Code pulled from `backend_testing` branch  
✅ Server restarted  
✅ Packages updated with correct credits  
✅ Subtitle shows actual credit amounts  
✅ API returns `subtitle` field  

## Admin Interface

Visit: `https://mifumosms.servehttp.com/admin/billing/smspackage/`

You should see:
- **Lite**: 5,000 credits ✅
- **Standard**: 50,000 credits (was 5,000) ✅
- **Pro**: 250,000 credits (was 5,000) ✅

## Rollback (if needed)

If something goes wrong:

```bash
# Rollback code
git reset --hard HEAD~1

# Restart server
sudo systemctl restart gunicorn
```

## Summary

**What Changed:**
1. Added `subtitle` property to show actual credits (5,000, 50,000, 250,000)
2. API now includes `subtitle` field
3. Fixed package data on live server (Standard: 50k, Pro: 250k)

**No database migrations needed** - the subtitle is a computed property!
