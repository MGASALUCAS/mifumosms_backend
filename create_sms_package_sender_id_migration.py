#!/usr/bin/env python3
"""
Create Migration for SMS Package Sender ID Fields
This script creates a Django migration for the new sender ID fields in SMSPackage
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import call_command

def create_migration():
    print("🔄 Creating Migration for SMS Package Sender ID Fields")
    print("=" * 60)
    
    try:
        # Create migration
        call_command('makemigrations', 'billing', name='add_sender_id_to_sms_package')
        print("✅ Migration created successfully!")
        
        # Show migration content
        print("\n📋 Migration created. You can now run:")
        print("   python manage.py migrate billing")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")

def main():
    print("📱 SMS Package Sender ID Migration")
    print("=" * 50)
    print("Adding sender ID functionality to SMS packages:")
    print("• default_sender_id - Default sender ID for the package")
    print("• allowed_sender_ids - List of allowed sender IDs")
    print("• sender_id_restriction - Restriction policy")
    print()
    
    create_migration()

if __name__ == "__main__":
    main()
