# Admin Dashboard Setup Guide

This guide will help you set up the Mifumo SMS Backend admin dashboard with sample data.

## Quick Setup (Recommended)

### Option 1: Automated Setup (Windows)
```bash
# Run the automated setup script
setup_admin.bat
```

### Option 2: Manual Setup
```bash
# 1. Create superuser with sample data
python create_admin_with_data.py

# 2. Start the server
python manage.py runserver
```

### Option 3: Step-by-Step Setup
```bash
# 1. Run migrations
python manage.py migrate

# 2. Create superuser only
python createsuperuser.py admin@mifumo.com Admin User admin123

# 3. Seed sample data
python seed_admin_data.py

# 4. Start the server
python manage.py runserver
```

## What Gets Created

The setup script will populate your admin dashboard with:

### 🏢 Tenants & Organizations
- **Mifumo Labs** (mifumo.com)
- **Tech Solutions Inc** (techsolutions.co.tz)
- **E-commerce Store** (ecommerce.co.tz)

### 👥 Users & Profiles
- **Admin User** (admin@mifumo.com) - Superuser
- **John Doe** (john@mifumo.com) - Staff user
- **Jane Smith** (jane@techsolutions.co.tz) - Regular user
- **Bob Johnson** (bob@ecommerce.co.tz) - Regular user

### 📞 Contacts & Messaging
- 8 sample contacts with phone numbers
- Sample conversations and messages
- SMS templates and campaigns

### 📱 SMS System
- **Beem Africa** SMS provider (primary)
- **Twilio** SMS provider (backup)
- 4 SMS packages (Starter, Business, Professional, Enterprise)
- 20+ sample SMS messages per tenant
- Sender name requests

### 💰 Billing & Subscriptions
- 2 billing plans (Basic, Professional)
- Active subscriptions for all tenants
- Usage records and payment history
- SMS packages with pricing

## Admin Dashboard Access

After setup, access the admin dashboard at:
- **URL**: http://localhost:8000/admin/
- **Email**: admin@mifumo.com
- **Password**: admin123

## Dashboard Sections

The admin dashboard will show populated data in:

### Authentication and Authorization
- **Groups**: User groups and permissions
- **Users**: All created users with profiles

### Tenants
- **Domains**: Custom domains for tenants
- **Memberships**: User-tenant associations
- **Tenants**: Organization information

### Messaging
- **Contacts**: Customer contact database
- **Conversations**: Message threads
- **Messages**: Individual messages
- **Templates**: Message templates
- **Campaigns**: Marketing campaigns
- **SMS Management**: SMS providers, packages, messages

### Billing
- **Billing Plans**: Subscription plans
- **Subscriptions**: Active subscriptions
- **SMS Packages**: Available packages
- **Usage Records**: Usage tracking
- **Billing Overview**: Financial summaries

## Customization

You can modify the sample data by editing:
- `seed_admin_data.py` - Main data seeding script
- `create_admin_with_data.py` - Superuser creation with data

## Troubleshooting

### Database Issues
```bash
# If you get database errors, run:
python manage.py migrate
python manage.py collectstatic --noinput
```

### Permission Issues
```bash
# Make sure the scripts are executable
chmod +x create_admin_with_data.py
chmod +x seed_admin_data.py
```

### Reset Data
```bash
# To reset all data and start fresh:
python manage.py flush
python create_admin_with_data.py
```

## Production Setup

For production deployment, use the production environment configuration:
1. Copy `production.env.example` to `.env`
2. Update database settings for PostgreSQL
3. Configure production API keys
4. Run migrations and collect static files

## Support

If you encounter any issues:
1. Check the Django logs for errors
2. Ensure all dependencies are installed
3. Verify database connectivity
4. Check environment configuration

The admin dashboard is now ready with comprehensive sample data for testing and demonstration!
