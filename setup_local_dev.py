#!/usr/bin/env python3
"""
Setup script for local development environment
This script helps set up the local development environment for Mifumo SMS Backend
"""

import os
import shutil
from pathlib import Path

def setup_local_development():
    """Set up local development environment"""
    print("🚀 Setting up Mifumo SMS Backend for local development...")
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        shutil.copy2('.env', '.env.backup')
    
    # Copy environment_config.env to .env
    if Path('environment_config.env').exists():
        shutil.copy2('environment_config.env', '.env')
        print("✅ Created .env file from environment_config.env")
    else:
        print("❌ environment_config.env not found!")
        return False
    
    # Check if db.sqlite3 exists
    if not Path('db.sqlite3').exists():
        print("📝 Database file doesn't exist. It will be created on first run.")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")
    print("\nYour server will be available at: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    setup_local_development()
