#!/usr/bin/env python3
"""
Create default notification templates for the notification system.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from notifications.models import NotificationTemplate

def create_notification_templates():
    """Create default notification templates."""
    print("Creating notification templates...")
    
    templates = [
        {
            'name': 'sms_credit_low',
            'title_template': 'Low SMS Credit Warning',
            'message_template': 'Your SMS credit is running low. You have {current_credits} credits remaining ({percentage:.1f}% of your total). Consider purchasing more credits to avoid service interruption.',
            'notification_type': 'sms_credit',
            'priority': 'medium',
            'variables': ['current_credits', 'percentage']
        },
        {
            'name': 'sms_credit_critical',
            'title_template': 'Critical: SMS Credit Very Low',
            'message_template': 'URGENT: Your SMS credit is critically low! You have only {current_credits} credits remaining ({percentage:.1f}% of your total). Purchase credits immediately to avoid service interruption.',
            'notification_type': 'sms_credit',
            'priority': 'urgent',
            'variables': ['current_credits', 'percentage']
        },
        {
            'name': 'campaign_sent',
            'title_template': 'Campaign Sent',
            'message_template': 'Your campaign "{campaign_name}" has been sent successfully to {recipient_count} recipients.',
            'notification_type': 'campaign',
            'priority': 'low',
            'variables': ['campaign_name', 'recipient_count']
        },
        {
            'name': 'campaign_failed',
            'title_template': 'Campaign Failed',
            'message_template': 'Your campaign "{campaign_name}" failed to send. Error: {error_message}',
            'notification_type': 'campaign',
            'priority': 'high',
            'variables': ['campaign_name', 'error_message']
        },
        {
            'name': 'contact_import_success',
            'title_template': 'Contact Import',
            'message_template': '{contact_count} contacts have been imported successfully from {source}.',
            'notification_type': 'contact',
            'priority': 'low',
            'variables': ['contact_count', 'source']
        },
        {
            'name': 'contact_import_failed',
            'title_template': 'Contact Import Failed',
            'message_template': 'Contact import failed. Error: {error_message}',
            'notification_type': 'contact',
            'priority': 'medium',
            'variables': ['error_message']
        },
        {
            'name': 'billing_payment_success',
            'title_template': 'Payment Successful',
            'message_template': 'Your payment of {amount} {currency} has been processed successfully. Transaction ID: {transaction_id}',
            'notification_type': 'billing',
            'priority': 'low',
            'variables': ['amount', 'currency', 'transaction_id']
        },
        {
            'name': 'billing_payment_failed',
            'title_template': 'Payment Failed',
            'message_template': 'Your payment of {amount} {currency} failed. Please try again or contact support. Error: {error_message}',
            'notification_type': 'billing',
            'priority': 'high',
            'variables': ['amount', 'currency', 'error_message']
        },
        {
            'name': 'security_login_alert',
            'title_template': 'New Login Detected',
            'message_template': 'A new login was detected from {ip_address} at {location} on {device}. If this was not you, please secure your account immediately.',
            'notification_type': 'security',
            'priority': 'medium',
            'variables': ['ip_address', 'location', 'device']
        },
        {
            'name': 'system_maintenance',
            'title_template': 'Scheduled Maintenance',
            'message_template': 'Scheduled maintenance will occur on {date} from {start_time} to {end_time}. Some features may be temporarily unavailable.',
            'notification_type': 'maintenance',
            'priority': 'medium',
            'variables': ['date', 'start_time', 'end_time']
        },
        {
            'name': 'system_error',
            'title_template': 'System Error',
            'message_template': 'A system error occurred: {error_message}. Our team has been notified and is working to resolve the issue.',
            'notification_type': 'error',
            'priority': 'high',
            'variables': ['error_message']
        },
        {
            'name': 'general_info',
            'title_template': '{title}',
            'message_template': '{message}',
            'notification_type': 'info',
            'priority': 'medium',
            'variables': ['title', 'message']
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for template_data in templates:
        template, created = NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        
        if created:
            created_count += 1
            print(f"Created template: {template_data['name']}")
        else:
            # Update existing template
            for key, value in template_data.items():
                setattr(template, key, value)
            template.save()
            updated_count += 1
            print(f"Updated template: {template_data['name']}")
    
    print(f"\nSummary:")
    print(f"Created: {created_count} templates")
    print(f"Updated: {updated_count} templates")
    print(f"Total: {created_count + updated_count} templates")

if __name__ == "__main__":
    create_notification_templates()
