#!/bin/bash
# Fix Static Files in Production
# Run this on your production server

echo "🔧 Fixing Static Files in Production..."

# Navigate to project directory
cd /root/mifumosms_backend

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=mifumo.settings
export DJANGO_DEBUG=False

echo "📊 Current static file settings:"
python manage.py shell << EOF
from django.conf import settings
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
EOF

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "📁 Checking collected files..."
ls -la staticfiles/
ls -la staticfiles/drf-yasg/ 2>/dev/null || echo "drf-yasg directory not found"

echo "🔍 Testing static file serving..."
python manage.py shell << EOF
from django.test import Client
client = Client()
response = client.get('/static/drf-yasg/style.css')
print(f"Static file response status: {response.status_code}")
if response.status_code == 200:
    print("✅ Static files are working")
else:
    print("❌ Static files need web server configuration")
EOF

echo "🎉 Static files fix completed!"
echo ""
echo "If you're still getting 404 errors for static files:"
echo "1. Make sure your web server (nginx/apache) is configured to serve static files"
echo "2. Check that STATIC_ROOT path is correct in your web server config"
echo "3. Restart your web server after making changes"
