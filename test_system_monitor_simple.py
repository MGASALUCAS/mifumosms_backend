#!/usr/bin/env python3
"""
Simple test for system monitor.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from notifications.system_monitor import SystemMonitor
from accounts.models import User

def test_system_monitor():
    """Test system monitor functionality."""
    print("Testing System Monitor...")
    
    try:
        system_monitor = SystemMonitor()
        
        # Test with a specific user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("ERROR: No admin user found")
            return
        
        print(f"Testing with user: {admin_user.email}")
        print(f"User tenant: {admin_user.get_tenant()}")
        
        # Test problem notification
        notification = system_monitor.create_problem_notification(
            problem_type="TEST_PROBLEM",
            description="This is a test problem notification",
            user=admin_user,
            priority="medium"
        )
        
        if notification:
            print(f"SUCCESS: Created notification {notification.id}")
            print(f"Title: {notification.title}")
            print(f"Message: {notification.message}")
            print(f"Tenant: {notification.tenant}")
        else:
            print("ERROR: Failed to create notification")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system_monitor()
