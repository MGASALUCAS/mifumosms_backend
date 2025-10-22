# Live Server Deployment Guide - Default Sender ID Fix

## 🚀 Pre-Deployment Checklist

### 1. **Backup Your Database**
```bash
# Create database backup before making changes
pg_dump your_database_name > backup_before_sender_id_fix.sql

# Or for MySQL
mysqldump -u username -p your_database_name > backup_before_sender_id_fix.sql

# Or for SQLite (if using SQLite)
cp db.sqlite3 db_backup_before_sender_id_fix.sqlite3
```

### 2. **Test in Staging Environment First**
```bash
# Deploy to staging server first
git checkout staging
git pull origin main
python manage.py migrate
python manage.py test
```

## 📦 Deployment Steps

### **Step 1: Deploy Code Changes**

```bash
# 1. Pull the latest changes
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Collect static files (if needed)
python manage.py collectstatic --noinput

# 6. Restart your web server
sudo systemctl restart nginx
sudo systemctl restart gunicorn
# or
sudo service apache2 restart
```

### **Step 2: Verify Migration Success**

```bash
# Check if migration was applied successfully
python manage.py showmigrations accounts

# You should see:
# [X] 0003_add_default_sender_ids

# Check the migration logs
python manage.py migrate accounts --verbosity=2
```

### **Step 3: Test the Fix**

```bash
# Run the test script to verify everything works
python test_default_sender_id.py

# Or test manually via API
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/messaging/sender-requests/default/overview/"
```

## 🔧 Server-Specific Instructions

### **For Django + Gunicorn + Nginx:**

```bash
# 1. Update code
cd /path/to/your/project
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 7. Check status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### **For Django + Apache + mod_wsgi:**

```bash
# 1. Update code
cd /path/to/your/project
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart Apache
sudo systemctl restart apache2
# or
sudo service apache2 restart

# 7. Check Apache logs
sudo tail -f /var/log/apache2/error.log
```

### **For Docker Deployment:**

```bash
# 1. Update your docker-compose.yml or Dockerfile if needed
# 2. Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d

# 3. Run migrations inside container
docker-compose exec web python manage.py migrate

# 4. Check logs
docker-compose logs -f web
```

## 🗄️ Database Migration Details

### **What the Migration Does:**

1. **Creates Default Sender IDs** for all existing tenants
2. **Creates SMS Providers** for tenants that don't have them
3. **Creates Sender ID Requests** for tracking purposes
4. **Handles Edge Cases** (tenants without owners)

### **Migration Output Example:**
```
Created default sender ID for tenant Company A
Created default sender ID request for tenant Company A
Tenant Company B already has default sender ID
No owner found for tenant Company C
Created default sender ID for tenant Company D
Skipped sender ID request for tenant Company C - no owner found
```

### **If Migration Fails:**

```bash
# Check migration status
python manage.py showmigrations accounts

# If migration is partially applied, you might need to:
# 1. Check database for any issues
# 2. Fix data inconsistencies
# 3. Re-run migration

# To rollback if needed (NOT RECOMMENDED in production)
# python manage.py migrate accounts 0002_alter_user_managers_remove_user_username
```

## 🔍 Post-Deployment Verification

### **1. API Endpoint Tests:**

```bash
# Test default sender overview
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/messaging/sender-requests/default/overview/"

# Expected response:
{
  "success": true,
  "data": {
    "default_sender": "Taarifa-SMS",
    "current_sender_id": "Taarifa-SMS",
    "is_available": true,
    "can_request": false,
    "reason": "Default sender already available."
  }
}
```

### **2. Database Verification:**

```sql
-- Check if all tenants have default sender IDs
SELECT t.name, s.sender_id, s.status 
FROM tenants_tenant t
LEFT JOIN sms_sender_ids s ON t.id = s.tenant_id 
WHERE s.sender_id = 'Taarifa-SMS';

-- Check sender ID requests
SELECT t.name, r.requested_sender_id, r.status
FROM tenants_tenant t
LEFT JOIN sender_id_requests r ON t.id = r.tenant_id
WHERE r.requested_sender_id = 'Taarifa-SMS';
```

### **3. Frontend Testing:**

1. **Login as a user**
2. **Check Default Sender ID card** - should show "Available"
3. **Check Quick SMS interface** - should show "Taarifa-SMS" in dropdown
4. **Verify no "No approved sender names" error**

## 🚨 Troubleshooting

### **Common Issues:**

#### **1. Migration Fails with Foreign Key Error:**
```bash
# Check if all required models exist
python manage.py shell
>>> from messaging.models_sms import SMSSenderID
>>> from messaging.models_sender_requests import SenderIDRequest
>>> from tenants.models import Tenant
```

#### **2. Users Still See "No approved sender names":**
```bash
# Check if sender IDs were created
python manage.py shell
>>> from messaging.models_sms import SMSSenderID
>>> SMSSenderID.objects.filter(sender_id='Taarifa-SMS', status='active').count()
```

#### **3. API Returns 500 Error:**
```bash
# Check server logs
tail -f /var/log/nginx/error.log
tail -f /var/log/gunicorn/error.log

# Check Django logs
python manage.py shell
>>> import logging
>>> logging.basicConfig(level=logging.DEBUG)
```

### **Rollback Plan (If Needed):**

```bash
# 1. Restore database backup
psql your_database_name < backup_before_sender_id_fix.sql

# 2. Revert code changes
git checkout HEAD~1

# 3. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 📊 Monitoring

### **1. Check Application Logs:**
```bash
# Monitor Django logs
tail -f /path/to/your/project/logs/django.log

# Monitor web server logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **2. Monitor Database:**
```sql
-- Check for any failed migrations
SELECT * FROM django_migrations WHERE app = 'accounts' AND name = '0003_add_default_sender_ids';

-- Check sender ID creation
SELECT COUNT(*) FROM sms_sender_ids WHERE sender_id = 'Taarifa-SMS';
```

### **3. Monitor API Performance:**
```bash
# Test API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://your-domain.com/api/messaging/sender-requests/default/overview/"

# Create curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#           time_total:  %{time_total}\n
```

## ✅ Success Criteria

### **After Deployment, Verify:**

1. ✅ **All existing users** have "Taarifa-SMS" available
2. ✅ **New user registration** automatically creates default sender ID
3. ✅ **API endpoints** return correct status
4. ✅ **Frontend** shows "Available" status for default sender ID
5. ✅ **No errors** in application logs
6. ✅ **Database** has correct sender ID records

### **Performance Impact:**
- **Minimal** - Only adds a few database records per tenant
- **One-time migration** - No ongoing performance impact
- **Faster user experience** - Users can start sending SMS immediately

## 📞 Support

If you encounter any issues during deployment:

1. **Check the logs** first
2. **Verify database** state
3. **Test API endpoints** manually
4. **Rollback** if necessary
5. **Contact support** with specific error messages

The fix is designed to be **safe and backward compatible**, so it should deploy smoothly on your live server.
