#!/usr/bin/env python3
"""
Check recent SMS failures to understand what changed
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.models_sms import SMSMessage
from django.utils import timezone
from datetime import timedelta

def check_recent_failures():
    """Check recent SMS failures to understand what changed."""
    print("=" * 80)
    print("CHECKING RECENT SMS FAILURES")
    print("=" * 80)
    
    try:
        # Get SMS messages from the last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        
        recent_messages = SMSMessage.objects.filter(
            created_at__gte=yesterday
        ).order_by('-created_at')
        
        print(f"Found {recent_messages.count()} SMS messages in the last 24 hours")
        
        # Group by status
        sent_count = recent_messages.filter(status='sent').count()
        failed_count = recent_messages.filter(status='failed').count()
        queued_count = recent_messages.filter(status='queued').count()
        
        print(f"  Sent: {sent_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Queued: {queued_count}")
        
        # Show recent failed messages
        if failed_count > 0:
            print("\n" + "=" * 80)
            print("RECENT FAILED MESSAGES")
            print("=" * 80)
            
            failed_messages = recent_messages.filter(status='failed')[:5]
            
            for message in failed_messages:
                print(f"\nFailed Message ID: {message.id}")
                print(f"  Created At: {message.created_at}")
                print(f"  Status: {message.status}")
                print(f"  Provider: {message.provider.name if message.provider else 'None'}")
                print(f"  Sender ID: {message.sender_id.sender_id if message.sender_id else 'None'}")
                print(f"  Error Message: {message.error_message}")
                print(f"  Error Code: {message.error_code}")
                print(f"  Provider Response: {message.provider_response}")
                print(f"  Base Message: {message.base_message.text[:50]}...")
                print(f"  Recipient: {message.base_message.recipient_number}")
        
        # Show recent successful messages
        if sent_count > 0:
            print("\n" + "=" * 80)
            print("RECENT SUCCESSFUL MESSAGES")
            print("=" * 80)
            
            sent_messages = recent_messages.filter(status='sent')[:5]
            
            for message in sent_messages:
                print(f"\nSuccessful Message ID: {message.id}")
                print(f"  Created At: {message.created_at}")
                print(f"  Status: {message.status}")
                print(f"  Provider: {message.provider.name if message.provider else 'None'}")
                print(f"  Sender ID: {message.sender_id.sender_id if message.sender_id else 'None'}")
                print(f"  Provider Response: {message.provider_response}")
                print(f"  Base Message: {message.base_message.text[:50]}...")
                print(f"  Recipient: {message.base_message.recipient_number}")
        
        # Check if there's a pattern in the timing
        print("\n" + "=" * 80)
        print("TIMING ANALYSIS")
        print("=" * 80)
        
        if sent_count > 0:
            last_successful = recent_messages.filter(status='sent').first()
            print(f"Last successful message: {last_successful.created_at}")
            print(f"  Sender ID: {last_successful.sender_id.sender_id if last_successful.sender_id else 'None'}")
            print(f"  Provider: {last_successful.provider.name if last_successful.provider else 'None'}")
        
        if failed_count > 0:
            first_failed = recent_messages.filter(status='failed').last()
            print(f"First failed message: {first_failed.created_at}")
            print(f"  Sender ID: {first_failed.sender_id.sender_id if first_failed.sender_id else 'None'}")
            print(f"  Provider: {first_failed.provider.name if first_failed.provider else 'None'}")
            print(f"  Error: {first_failed.error_message}")
        
    except Exception as e:
        print(f"Error checking recent failures: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run failure analysis."""
    print("Checking Recent SMS Failures")
    print("=" * 80)
    
    check_recent_failures()

if __name__ == "__main__":
    main()
