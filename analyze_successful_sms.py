#!/usr/bin/env python3
"""
Analyze successful SMS messages from yesterday to understand the correct format
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

def analyze_successful_sms():
    """Analyze successful SMS messages to understand the correct format."""
    print("=" * 80)
    print("ANALYZING SUCCESSFUL SMS MESSAGES")
    print("=" * 80)
    
    try:
        # Get SMS messages from yesterday
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        
        successful_messages = SMSMessage.objects.filter(
            created_at__gte=yesterday,
            created_at__lt=today,
            status='sent'
        ).order_by('-created_at')
        
        print(f"Found {successful_messages.count()} successful SMS messages from yesterday")
        
        for message in successful_messages[:5]:  # Show first 5
            print(f"\nMessage ID: {message.id}")
            print(f"  Status: {message.status}")
            print(f"  Provider: {message.provider.name if message.provider else 'None'}")
            print(f"  Sender ID: {message.sender_id.sender_id if message.sender_id else 'None'}")
            print(f"  Provider Message ID: {message.provider_message_id}")
            print(f"  Provider Request ID: {message.provider_request_id}")
            print(f"  Provider Response: {message.provider_response}")
            print(f"  Sent At: {message.sent_at}")
            print(f"  Base Message: {message.base_message.text[:50]}...")
            print(f"  Recipient: {message.base_message.recipient_number}")
        
        # Check if there are any patterns in the provider_response
        print("\n" + "=" * 80)
        print("ANALYZING PROVIDER RESPONSES")
        print("=" * 80)
        
        for message in successful_messages[:3]:
            if message.provider_response:
                print(f"\nMessage {message.id} Provider Response:")
                print(f"  {message.provider_response}")
        
        # Check recent failed messages to see the error pattern
        print("\n" + "=" * 80)
        print("ANALYZING RECENT FAILED MESSAGES")
        print("=" * 80)
        
        failed_messages = SMSMessage.objects.filter(
            created_at__gte=yesterday,
            created_at__lt=today,
            status='failed'
        ).order_by('-created_at')
        
        print(f"Found {failed_messages.count()} failed SMS messages from yesterday")
        
        for message in failed_messages[:3]:
            print(f"\nFailed Message ID: {message.id}")
            print(f"  Status: {message.status}")
            print(f"  Error Message: {message.error_message}")
            print(f"  Error Code: {message.error_code}")
            print(f"  Provider Response: {message.provider_response}")
        
    except Exception as e:
        print(f"Error analyzing SMS messages: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run SMS analysis."""
    print("Analyzing Successful SMS Messages")
    print("=" * 80)
    
    analyze_successful_sms()

if __name__ == "__main__":
    main()
