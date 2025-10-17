#!/bin/bash
# Production Migration Commands
# Run these commands on your production server

echo "🔧 Starting Production Database Migration..."

# Navigate to project directory
cd /root/mifumosms_backend

# Activate virtual environment
source venv/bin/activate

# Set environment variables for production
export DJANGO_SETTINGS_MODULE=mifumo.settings
export DJANGO_DEBUG=False

echo "📊 Checking current database status..."

# Check if database file exists
if [ -f "db.sqlite3" ]; then
    echo "✅ Database file exists"
    ls -la db.sqlite3
else
    echo "ℹ️  Database file not found, will be created"
fi

echo "🔄 Running Django migrations..."

# Create migrations for all apps
python manage.py makemigrations

# Apply migrations
python manage.py migrate

echo "🌐 Creating Site data..."

# Create site data using Django shell
python manage.py shell << EOF
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': '196.249.97.239:8000',
        'name': 'Mifumo WMS Production'
    }
)
if created:
    print(f"✅ Created site: {site.domain}")
else:
    print(f"ℹ️  Site already exists: {site.domain}")
EOF

echo "👤 Creating superuser..."

# Create superuser (non-interactive)
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@mifumo.com',
        password='admin123',  # Change this password!
        first_name='Admin',
        last_name='User'
    )
    print("✅ Superuser created: admin@mifumo.com/admin123")
else:
    print("ℹ️  Superuser already exists")
EOF

echo "🔍 Testing admin access..."

# Test admin access
python manage.py shell << EOF
from django.test import Client
client = Client()
response = client.get('/admin/login/')
print(f"Admin login status: {response.status_code}")
if response.status_code == 200:
    print("✅ Admin login page accessible")
else:
    print("❌ Admin login page not accessible")
EOF

echo "🎉 Migration completed!"
echo ""
echo "Next steps:"
echo "1. Restart your Django server"
echo "2. Access http://196.249.97.239:8000/admin/login/"
echo "3. Login with admin@mifumo.com/admin123 (change password immediately!)"
