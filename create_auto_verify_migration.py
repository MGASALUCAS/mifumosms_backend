#!/usr/bin/env python3
"""
Create migration to automatically verify superadmin and staff users
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import call_command
from django.db import migrations, models

def create_auto_verify_migration():
    """Create migration to automatically verify superadmin and staff users."""
    print("=" * 80)
    print("CREATING MIGRATION FOR AUTO-VERIFY SUPERADMIN/STAFF USERS")
    print("=" * 80)
    
    try:
        # Create a custom migration file
        migration_content = '''"""
Auto-verify superadmin and staff users
"""
from django.db import migrations

def auto_verify_superadmin_staff(apps, schema_editor):
    """Mark all superadmin and staff users as phone verified."""
    User = apps.get_model('accounts', 'User')
    
    # Update superadmin users
    superadmin_users = User.objects.filter(is_superuser=True)
    superadmin_updated = 0
    for user in superadmin_users:
        if not user.phone_verified:
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])
            superadmin_updated += 1
    
    # Update staff users (excluding superadmin to avoid duplicates)
    staff_users = User.objects.filter(is_staff=True, is_superuser=False)
    staff_updated = 0
    for user in staff_users:
        if not user.phone_verified:
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])
            staff_updated += 1
    
    print(f"Auto-verified {superadmin_updated} superadmin users")
    print(f"Auto-verified {staff_updated} staff users")

def reverse_auto_verify(apps, schema_editor):
    """Reverse the auto-verification (set phone_verified to False)."""
    User = apps.get_model('accounts', 'User')
    
    # This is optional - you might not want to reverse this
    # User.objects.filter(is_superuser=True).update(phone_verified=False)
    # User.objects.filter(is_staff=True, is_superuser=False).update(phone_verified=False)
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_make_phone_number_unique'),
    ]

    operations = [
        migrations.RunPython(auto_verify_superadmin_staff, reverse_auto_verify),
    ]
'''
        
        # Write migration file
        migration_file = 'accounts/migrations/0007_auto_verify_superadmin_staff.py'
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        print(f"Created migration file: {migration_file}")
        
        # Run the migration
        print("Running migration...")
        call_command('migrate', 'accounts', verbosity=2)
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error creating migration: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the migration creation."""
    print("Creating Migration for Auto-Verify Superadmin/Staff Users")
    print("=" * 80)
    
    create_auto_verify_migration()

if __name__ == "__main__":
    main()
