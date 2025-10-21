#!/usr/bin/env python
"""
Test script to send SMS and check balance reduction
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from messaging.models_sms import SMSSenderID, SMSProvider
from messaging.services.sms_validation import SMSValidationService
from messaging.services.beem_sms import BeemSMSService
from billing.models import SMSBalance
import logging

User = get_user_model()

def send_test_sms():
    """Send a test SMS and verify balance reduction"""
    
    # Get the first admin user and their tenant
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No admin user found!")
        return
    
    tenant = admin_user.tenant
    if not tenant:
        print("❌ Admin user has no tenant!")
        return
    
    print(f"Using admin user: {admin_user.email}")
    print(f"Using tenant: {tenant.name}")
    
    # Check current SMS balance
    try:
        sms_balance = SMSBalance.objects.get(tenant=tenant)
        print(f"Current SMS balance: {sms_balance.credits} credits")
    except SMSBalance.DoesNotExist:
        print("No SMS balance found for tenant!")
        return
    
    # Get the Taarifa-SMS sender ID
    try:
        sender_id = SMSSenderID.objects.get(
            tenant=tenant,
            sender_id='Taarifa-SMS',
            status='active'
        )
        print(f"Using sender ID: {sender_id.sender_id}")
    except SMSSenderID.DoesNotExist:
        print("Taarifa-SMS sender ID not found!")
        return
    
    # Get Beem provider
    try:
        provider = SMSProvider.objects.get(
            tenant=tenant,
            provider_type='beem',
            is_active=True
        )
        print(f"Using provider: {provider.name}")
    except SMSProvider.DoesNotExist:
        print("Beem provider not found!")
        return
    
    # Test message
    message = "Hello! This is a test message from Mifumo SMS system. Your SMS service is working correctly!"
    phone_number = "255757347863"  # Tanzanian number format
    
    print(f"Message: {message}")
    print(f"Phone: {phone_number}")
    
    # Initialize SMS service
    beem_service = BeemSMSService()
    
    # Check if we can send (validation)
    validation_service = SMSValidationService(tenant)
    validation_result = validation_service.validate_sms_sending(
        sender_id.sender_id,
        required_credits=1
    )
    
    if not validation_result['valid']:
        print(f"Validation failed: {validation_result['error']}")
        return
    
    print("Validation passed - can send SMS")
    
    # Send SMS
    print("Sending SMS...")
    try:
        response = beem_service.send_sms(
            message=message,
            recipients=[phone_number],
            source_addr=sender_id.sender_id
        )
        
        if response.get('success'):
            print("SMS sent successfully!")
            print(f"Response: {response}")
            
            # Deduct credits
            try:
                validation_service.deduct_credits(
                    amount=1,
                    sender_id=sender_id.sender_id,
                    message_id="test_message_001",
                    description=f"Test SMS to {phone_number}"
                )
                print("Credits deducted successfully!")
                
                # Check new balance
                sms_balance.refresh_from_db()
                print(f"New SMS balance: {sms_balance.credits} credits")
                
            except Exception as e:
                print(f"Failed to deduct credits: {e}")
        else:
            print(f"SMS sending failed: {response}")
            
    except Exception as e:
        print(f"Error sending SMS: {e}")

if __name__ == "__main__":
    send_test_sms()
