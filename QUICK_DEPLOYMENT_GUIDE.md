# Quick Deployment Guide - Default Sender ID Fix

## 🚀 **Quick Start (5 Minutes)**

### **For Most Servers:**

```bash
# 1. Backup database (IMPORTANT!)
pg_dump your_database > backup_$(date +%Y%m%d).sql

# 2. Update code
cd /path/to/your/project
git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migration
python manage.py migrate

# 6. Restart server
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### **For Docker:**

```bash
# 1. Update code
git pull origin main

# 2. Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# 3. Run migration
docker-compose exec web python manage.py migrate
```

## 🔍 **Verify It Worked:**

```bash
# Check migration
python manage.py showmigrations accounts | grep "0003_add_default_sender_ids"

# Check sender IDs
python manage.py shell -c "from messaging.models_sms import SMSSenderID; print(SMSSenderID.objects.filter(sender_id='Taarifa-SMS').count())"

# Test API
curl "https://your-domain.com/api/messaging/sender-requests/default/overview/"
```

## ✅ **Expected Results:**

- **Migration shows `[X]`** ✅
- **Sender ID count > 0** ✅  
- **API returns `"is_available": true`** ✅

## 🚨 **If Something Goes Wrong:**

```bash
# Rollback database
psql your_database < backup_$(date +%Y%m%d).sql

# Revert code
git checkout HEAD~1

# Restart server
sudo systemctl restart gunicorn
```

## 📞 **Need Help?**

1. **Check logs**: `tail -f /var/log/nginx/error.log`
2. **Test manually**: Use the verification script
3. **Rollback**: Restore database backup

The fix is **safe** and **backward compatible** - it only adds data, doesn't change existing functionality.
