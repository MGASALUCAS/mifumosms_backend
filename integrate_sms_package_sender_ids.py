#!/usr/bin/env python3
"""
Integrate SMS Package Sender ID Logic
This script shows how to integrate sender ID logic with SMS packages
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage, SMSBalance
from messaging.services.sms_service import SMSService
from tenants.models import Tenant

def send_sms_with_package_validation(tenant_id, to, message, sender_id=None, package_id=None):
    """
    Send SMS with package-based sender ID validation.
    
    Args:
        tenant_id (str): Tenant ID
        to (str): Phone number
        message (str): SMS message
        sender_id (str, optional): Requested sender ID
        package_id (str, optional): Specific package to use for validation
        
    Returns:
        dict: SMS sending result
    """
    print(f"📱 Sending SMS with Package Validation")
    print(f"   Tenant: {tenant_id}")
    print(f"   To: {to}")
    print(f"   Message: {message}")
    print(f"   Requested Sender ID: {sender_id}")
    print(f"   Package ID: {package_id}")
    
    # Get tenant
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return {
            'success': False,
            'error': 'Tenant not found'
        }
    
    # Get SMS balance to determine package
    try:
        sms_balance = SMSBalance.objects.get(tenant=tenant)
    except SMSBalance.DoesNotExist:
        return {
            'success': False,
            'error': 'No SMS balance found for tenant'
        }
    
    # Get the package (either specified or most recent purchase)
    if package_id:
        try:
            package = SMSPackage.objects.get(id=package_id)
        except SMSPackage.DoesNotExist:
            return {
                'success': False,
                'error': 'Package not found'
            }
    else:
        # Get the most recent active package (you might want to implement this logic)
        package = SMSPackage.objects.filter(is_active=True).first()
        if not package:
            return {
                'success': False,
                'error': 'No active SMS package found'
            }
    
    print(f"   Using Package: {package.name} ({package.package_type})")
    print(f"   Package Sender ID Config:")
    print(f"     - Default: {package.default_sender_id}")
    print(f"     - Restriction: {package.sender_id_restriction}")
    print(f"     - Allowed List: {package.allowed_sender_ids}")
    
    # Validate and get effective sender ID
    effective_sender_id = package.get_effective_sender_id(sender_id)
    
    if not effective_sender_id:
        return {
            'success': False,
            'error': f'No valid sender ID available for package {package.name}'
        }
    
    print(f"   Effective Sender ID: {effective_sender_id}")
    
    # Check if sender ID is allowed
    if not package.is_sender_id_allowed(sender_id) and sender_id:
        print(f"   ⚠️  Requested sender ID '{sender_id}' not allowed, using '{effective_sender_id}'")
    
    # Check if tenant has enough credits
    if sms_balance.credits < 1:
        return {
            'success': False,
            'error': 'Insufficient SMS credits'
        }
    
    # Send SMS
    try:
        sms_service = SMSService(tenant_id=tenant_id)
        result = sms_service.send_sms(
            to=to,
            message=message,
            sender_id=effective_sender_id
        )
        
        # If successful, deduct credits
        if result.get('success'):
            sms_balance.use_credits(1)
            print(f"   ✅ SMS sent successfully! Credits remaining: {sms_balance.credits}")
        else:
            print(f"   ❌ SMS failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ SMS sending error: {e}")
        return {
            'success': False,
            'error': f'SMS sending failed: {str(e)}'
        }

def test_package_sender_id_logic():
    """Test the package sender ID logic with different scenarios."""
    print("\nTesting Package Sender ID Logic")
    print("=" * 50)
    
    # Get a test tenant
    tenant = Tenant.objects.filter(subdomain='default').first()
    if not tenant:
        print("ERROR: No test tenant found!")
        return
    
    # Get packages
    packages = SMSPackage.objects.all()
    
    for package in packages:
        print(f"\nTesting Package: {package.name}")
        print(f"   Type: {package.package_type}")
        print(f"   Default Sender ID: {package.default_sender_id}")
        print(f"   Restriction: {package.sender_id_restriction}")
        print(f"   Allowed List: {package.allowed_sender_ids}")
        
        # Test different sender IDs
        test_cases = [
            ('Taarifa-SMS', 'Should work'),
            ('Quantum', 'Should work'),
            ('MIFUMO', 'Should fail or fallback'),
            (None, 'Should use default'),
            ('CustomID', 'Should fail or fallback')
        ]
        
        for sender_id, description in test_cases:
            effective = package.get_effective_sender_id(sender_id)
            is_allowed = package.is_sender_id_allowed(sender_id)
            status = "PASS" if is_allowed else "WARN"
            
            print(f"   {status} {sender_id or 'None'}: {description}")
            print(f"      Allowed: {is_allowed}, Effective: {effective}")

def main():
    print("SMS Package Sender ID Integration")
    print("=" * 50)
    print("This demonstrates how to integrate sender ID logic with SMS packages:")
    print("- Package-based sender ID validation")
    print("- Automatic fallback to default sender ID")
    print("- Credit deduction after successful send")
    print("- Error handling for invalid sender IDs")
    print()
    
    # Test the logic
    test_package_sender_id_logic()
    
    print("\nIntegration Points:")
    print("1. Add this logic to your SMS sending API endpoints")
    print("2. Update your frontend to show available sender IDs per package")
    print("3. Add sender ID selection in your SMS sending forms")
    print("4. Implement package-based pricing based on sender ID restrictions")

if __name__ == "__main__":
    main()
