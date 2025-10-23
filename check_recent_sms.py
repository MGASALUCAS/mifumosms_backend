#!/usr/bin/env python3
"""
Check recent SMS messages to see what's working
"""

import os
import sys
import django
from datetime import timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.models_sms import SMSMessage
from django.utils import timezone

def check_recent_sms():
    """Check recent SMS messages."""
    print("=" * 80)
    print("CHECKING RECENT SMS MESSAGES")
    print("=" * 80)
    
    # Check last 24 hours
    recent = SMSMessage.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    )
    
    print(f"Recent SMS messages (last 24h): {recent.count()}")
    print(f"Successful: {recent.filter(status='sent').count()}")
    print(f"Failed: {recent.filter(status='failed').count()}")
    print(f"Queued: {recent.filter(status='queued').count()}")
    
    # Show recent successful messages
    successful = recent.filter(status='sent')[:5]
    print(f"\nRecent successful messages:")
    for msg in successful:
        print(f"  ID: {msg.id}")
        print(f"  Sender: {msg.sender_id.sender_id}")
        print(f"  Status: {msg.status}")
        print(f"  Created: {msg.created_at}")
        print(f"  Provider: {msg.provider.name}")
        print()
    
    # Show recent failed messages
    failed = recent.filter(status='failed')[:5]
    print(f"Recent failed messages:")
    for msg in failed:
        print(f"  ID: {msg.id}")
        print(f"  Sender: {msg.sender_id.sender_id}")
        print(f"  Status: {msg.status}")
        print(f"  Error: {msg.error_message}")
        print(f"  Created: {msg.created_at}")
        print()

def check_all_sms():
    """Check all SMS messages."""
    print("\n" + "=" * 80)
    print("CHECKING ALL SMS MESSAGES")
    print("=" * 80)
    
    all_sms = SMSMessage.objects.all()
    print(f"Total SMS messages: {all_sms.count()}")
    print(f"Successful: {all_sms.filter(status='sent').count()}")
    print(f"Failed: {all_sms.filter(status='failed').count()}")
    print(f"Queued: {all_sms.filter(status='queued').count()}")
    
    # Show all successful messages
    successful = all_sms.filter(status='sent')
    print(f"\nAll successful messages:")
    for msg in successful:
        print(f"  ID: {msg.id}")
        print(f"  Sender: {msg.sender_id.sender_id}")
        print(f"  Status: {msg.status}")
        print(f"  Created: {msg.created_at}")
        print(f"  Provider: {msg.provider.name}")
        print()

def main():
    """Run all checks."""
    print("Checking SMS Messages")
    print("=" * 80)
    
    check_recent_sms()
    check_all_sms()

if __name__ == "__main__":
    main()
