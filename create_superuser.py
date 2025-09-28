#!/usr/bin/env python
"""
Script to create a superuser for Mifumo WMS with custom user model.
This handles the custom user model that uses email as username.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

def create_superuser():
    """Create a superuser with the custom user model."""
    User = get_user_model()
    
    # Superuser details
    email = 'admin@mifumo.com'
    password = 'admin123'
    first_name = 'Admin'
    last_name = 'User'
    
    try:
        # Check if superuser already exists
        if User.objects.filter(email=email).exists():
            print(f"❌ Superuser with email '{email}' already exists!")
            return False
        
        # Create superuser
        superuser = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        print("✅ Superuser created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🆔 User ID: {superuser.id}")
        
        return True
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def create_tenant():
    """Create a default tenant for the superuser."""
    try:
        from tenants.models import Tenant
        
        # Check if tenant already exists
        if Tenant.objects.filter(subdomain='admin').exists():
            print("ℹ️  Default tenant already exists!")
            return True
        
        # Create default tenant
        tenant = Tenant.objects.create(
            name='Mifumo Admin',
            subdomain='admin',
            domain='admin.mifumo.com',
            is_active=True
        )
        
        print("✅ Default tenant created successfully!")
        print(f"🏢 Tenant: {tenant.name}")
        print(f"🌐 Subdomain: {tenant.subdomain}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tenant: {e}")
        return False

def assign_tenant_to_user():
    """Assign the default tenant to the superuser."""
    try:
        from tenants.models import Tenant
        User = get_user_model()
        
        # Get the superuser and tenant
        user = User.objects.get(email='admin@mifumo.com')
        tenant = Tenant.objects.get(subdomain='admin')
        
        # Assign tenant to user
        user.tenant = tenant
        user.save()
        
        print("✅ Tenant assigned to superuser successfully!")
        print(f"👤 User: {user.email}")
        print(f"🏢 Tenant: {tenant.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error assigning tenant: {e}")
        return False

def main():
    """Main function to set up superuser and tenant."""
    print("🚀 Setting up Mifumo WMS superuser...")
    print("=" * 50)
    
    # Create superuser
    if not create_superuser():
        print("❌ Failed to create superuser!")
        return False
    
    print()
    
    # Create tenant
    if not create_tenant():
        print("❌ Failed to create tenant!")
        return False
    
    print()
    
    # Assign tenant to user
    if not assign_tenant_to_user():
        print("❌ Failed to assign tenant to user!")
        return False
    
    print()
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("📧 Login with: admin@mifumo.com")
    print("🔑 Password: admin123")
    print("🌐 Access: http://localhost:8000/admin/")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
