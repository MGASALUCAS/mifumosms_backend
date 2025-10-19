#!/usr/bin/env python3
"""
Enhanced superuser creation script with sample data seeding
Creates a superuser and populates the admin dashboard with sample data
"""

import sys
import os
import django
from django.contrib.auth import get_user_model
from django.core.management import call_command

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

User = get_user_model()

def create_superuser_with_data():
    """Create superuser and seed sample data"""
    print("🚀 Creating superuser with sample data for Mifumo SMS Backend...")
    print("=" * 60)
    
    # Default admin credentials
    admin_email = "admin@mifumo.com"
    admin_password = "admin123"
    admin_first_name = "Admin"
    admin_last_name = "User"
    
    try:
        # Check if superuser already exists
        if User.objects.filter(email=admin_email).exists():
            print(f"ℹ️  Superuser with email {admin_email} already exists")
            user = User.objects.get(email=admin_email)
        else:
            # Create superuser
            print(f"👤 Creating superuser: {admin_email}")
            user = User.objects.create_superuser(
                email=admin_email,
                username=admin_email,
                first_name=admin_first_name,
                last_name=admin_last_name,
                password=admin_password
            )
            print(f"✅ Superuser created successfully!")
        
        # Run migrations first
        print("\n🔄 Running database migrations...")
        call_command('migrate', verbosity=0)
        print("✅ Migrations completed")
        
        # Seed sample data
        print("\n🌱 Seeding sample data...")
        from seed_admin_data import seed_all_data
        seed_all_data()
        
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print("\nAdmin Dashboard Access:")
        print(f"🌐 URL: http://localhost:8000/admin/")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Password: {admin_password}")
        print("\nDashboard now contains sample data for:")
        print("  🏢 Tenants and Domains")
        print("  👥 Users and Profiles")
        print("  📞 Contacts and Conversations")
        print("  📱 SMS Providers and Messages")
        print("  📦 SMS Packages and Billing")
        print("  💰 Subscriptions and Usage Records")
        print("\nStart the server with: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_superuser_with_data()
