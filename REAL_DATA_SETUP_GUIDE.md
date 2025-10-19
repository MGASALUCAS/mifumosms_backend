# Real Data Setup Guide - Production Ready

This guide sets up **REAL, FUNCTIONAL** data for your Mifumo SMS Backend using actual Beem SMS API integration.

## 🎯 What You Get

**Real, working data that actually functions:**

- ✅ **Real Beem SMS API integration** with your actual credentials
- ✅ **Real sender IDs** fetched from your Beem account
- ✅ **Real account balance** checking
- ✅ **Real SMS sending capability** that actually works
- ✅ **Production SMS packages** with actual Tanzanian pricing
- ✅ **Real billing system** with subscriptions and usage tracking
- ✅ **SMS templates** for common business use cases
- ✅ **Multi-user support** with proper permissions

## 🚀 Quick Setup

### Option 1: Production-Ready Setup (Recommended)
```bash
# Set up everything with real data
python setup_production_ready.py

# Test real SMS functionality
python test_real_sms.py
```

### Option 2: Basic Real Data Setup
```bash
# Set up basic real data
python setup_real_data.py

# Test SMS sending
python test_real_sms.py
```

## 📋 Prerequisites

1. **Beem SMS API Credentials** (already configured in your environment)
2. **Django environment** properly set up
3. **Database** (SQLite for local, PostgreSQL for production)

## 🔧 What Gets Created

### 🏢 Real Business Data
- **Mifumo Labs** tenant with real business information
- **Production domains** (mifumo.com, app.mifumo.com, api.mifumo.com)
- **Real users** with proper roles and permissions

### 📱 Real SMS System
- **Beem Africa SMS Provider** with your actual API credentials
- **Real sender IDs** fetched from your Beem account
- **Account balance** checking and monitoring
- **SMS sending capability** that actually works

### 📦 Real SMS Packages
- **Starter Pack**: 100 SMS for TZS 5,000 (TZS 50 per SMS)
- **Business Pack**: 500 SMS for TZS 20,000 (TZS 40 per SMS) - Popular
- **Professional Pack**: 1,000 SMS for TZS 35,000 (TZS 35 per SMS)
- **Enterprise Pack**: 5,000 SMS for TZS 150,000 (TZS 30 per SMS)

### 💰 Real Billing System
- **Active subscription** for the tenant
- **SMS balance** with 1,000 credits
- **Usage tracking** and billing records
- **Payment history** and invoices

### 📝 Real SMS Templates
- **Welcome Message**: For new customers
- **Order Confirmation**: For e-commerce
- **Appointment Reminder**: For bookings
- **Payment Confirmation**: For transactions
- **OTP Code**: For authentication

## 🧪 Testing Real SMS

After setup, test the real SMS functionality:

```bash
python test_real_sms.py
```

This will:
1. Check your Beem account balance
2. List available sender IDs
3. Send a test SMS (you'll be prompted for a phone number)
4. Check delivery reports

## 📊 Admin Dashboard

Access the admin dashboard at: http://localhost:8000/admin/

**Login Credentials:**
- **Email**: admin@mifumo.com
- **Password**: password123

**Dashboard Sections with Real Data:**
- **Tenants**: Real business information
- **SMS Providers**: Your actual Beem configuration
- **SMS Packages**: Real packages with actual pricing
- **SMS Messages**: Real message sending capability
- **Billing**: Active subscriptions and usage
- **Templates**: Ready-to-use SMS templates

## 🔄 Real SMS Workflow

1. **Send SMS** through the admin interface or API
2. **Real delivery** via Beem SMS API
3. **Delivery reports** automatically updated
4. **Usage tracking** and billing updates
5. **Balance monitoring** and alerts

## 🛠️ Customization

### Add More Sender IDs
```python
# In Django shell or admin
from messaging.models_sms import SMSSenderID
from tenants.models import Tenant

tenant = Tenant.objects.get(subdomain='mifumo')
SMSSenderID.objects.create(
    tenant=tenant,
    sender_id='YOUR_SENDER_ID',
    status='active',
    is_approved=True
)
```

### Create Custom SMS Packages
```python
# In Django shell or admin
from billing.models import SMSPackage

SMSPackage.objects.create(
    name='Custom Pack',
    package_type='custom',
    credits=2000,
    price=Decimal('60000.00'),
    unit_price=Decimal('30.00'),
    is_active=True,
    features=['Custom features'],
    sender_id_restriction='none'
)
```

### Add SMS Templates
```python
# In Django shell or admin
from messaging.models_sms import SMSTemplate
from tenants.models import Tenant

tenant = Tenant.objects.get(subdomain='mifumo')
SMSTemplate.objects.create(
    tenant=tenant,
    name='Custom Template',
    content='Your custom message with {variable}',
    category='custom',
    is_active=True
)
```

## 🚨 Troubleshooting

### Beem API Issues
```bash
# Check API credentials
python -c "from django.conf import settings; print('API Key:', settings.BEEM_API_KEY[:10] + '...')"

# Test API connection
python test_real_sms.py
```

### Database Issues
```bash
# Reset and recreate
python manage.py flush
python setup_production_ready.py
```

### SMS Sending Issues
1. Check Beem account balance
2. Verify sender ID is approved
3. Check phone number format (+255...)
4. Review Beem API logs

## 📈 Production Deployment

For production deployment:

1. **Update environment** with production settings
2. **Configure PostgreSQL** database
3. **Set up SSL** for webhooks
4. **Configure production** Beem credentials
5. **Set up monitoring** and logging

## 🎉 Result

Your admin dashboard now contains **REAL, FUNCTIONAL** data that actually works for sending SMS messages through your Beem SMS account. No more empty sections - everything is populated with real, working data!

**Ready to send real SMS messages right away!** 🚀
