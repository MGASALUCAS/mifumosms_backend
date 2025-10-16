#!/usr/bin/env python
"""
Test script to verify ZenoPay authentication is working correctly.
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import zenopay_service
from django.conf import settings

def test_zenopay_configuration():
    """Test ZenoPay configuration and authentication."""
    print("=" * 60)
    print("ZENOPAY CONFIGURATION TEST")
    print("=" * 60)
    
    # Check if API key is configured
    api_key = getattr(settings, 'ZENOPAY_API_KEY', '')
    print(f"ZENOPAY_API_KEY: {'✓ Configured' if api_key else '✗ Not configured'}")
    print(f"API Key value: {api_key[:10]}..." if api_key else "API Key value: (empty)")
    
    # Check timeout setting
    timeout = getattr(settings, 'ZENOPAY_API_TIMEOUT', 30)
    print(f"ZENOPAY_API_TIMEOUT: {timeout}")
    
    # Check base URL
    base_url = getattr(settings, 'BASE_URL', '')
    print(f"BASE_URL: {base_url}")
    
    # Test service initialization
    print(f"\nZenoPay Service initialized: {'✓' if zenopay_service else '✗'}")
    print(f"Service API Key: {zenopay_service.api_key[:10]}..." if zenopay_service.api_key else "Service API Key: (empty)")
    print(f"Service Base URL: {zenopay_service.base_url}")
    print(f"Service Timeout: {zenopay_service.timeout}")
    
    # Test headers generation
    headers = zenopay_service._get_headers()
    print(f"\nGenerated Headers:")
    for key, value in headers.items():
        if key == 'x-api-key':
            print(f"  {key}: {value[:10]}..." if value else f"  {key}: (empty)")
        else:
            print(f"  {key}: {value}")
    
    # Test phone number validation
    test_phone = "0614853618"
    formatted_phone = zenopay_service._validate_phone_number(test_phone)
    print(f"\nPhone Number Validation:")
    print(f"  Input: {test_phone}")
    print(f"  Formatted: {formatted_phone}")
    
    print("\n" + "=" * 60)
    print("CONFIGURATION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_zenopay_configuration()
