#!/usr/bin/env python3
"""
Test Script for Beem SMS Integration

This script provides comprehensive testing for the Beem SMS API integration.
It includes connection testing, SMS sending, and validation functionality.

Usage:
    python test_sms_beem.py

Requirements:
    - Django environment must be set up
    - Beem API credentials must be configured
    - Database must be migrated
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings
from messaging.services.beem_sms import BeemSMSService, BeemSMSError


class BeemSMSTester:
    """Test class for Beem SMS functionality"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/messaging/sms/beem"
        self.test_phone = "255700000001"  # Test phone number
        self.test_message = "Test message from Mifumo WMS - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def test_connection(self):
        """Test connection to Beem API"""
        print("🔗 Testing Beem Connection...")
        try:
            service = BeemSMSService()
            result = service.test_connection()
            
            if result.get('success'):
                print("✅ Connection test successful!")
                print(f"   API Key configured: {result.get('api_key_configured', False)}")
                print(f"   Secret Key configured: {result.get('secret_key_configured', False)}")
            else:
                print("❌ Connection test failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
            return result.get('success', False)
        except Exception as e:
            print(f"❌ Connection test error: {str(e)}")
            return False
    
    def test_phone_validation(self):
        """Test phone number validation"""
        print("\n📱 Testing Phone Number Validation...")
        try:
            service = BeemSMSService()
            
            test_numbers = [
                "255700000001",  # Valid Tanzania
                "+255700000001",  # Valid with +
                "0700000001",     # Invalid (missing country code)
                "255-700-000-001", # Invalid (contains dashes)
                "123456789",      # Invalid (too short)
            ]
            
            for phone in test_numbers:
                is_valid = service.validate_phone_number(phone)
                formatted = service._format_phone_number(phone)
                status = "✅" if is_valid else "❌"
                print(f"   {status} {phone} -> {formatted} (Valid: {is_valid})")
                
            return True
        except Exception as e:
            print(f"❌ Phone validation error: {str(e)}")
            return False
    
    def test_send_sms(self):
        """Test sending SMS via API"""
        print("\n📤 Testing SMS Sending...")
        try:
            # Note: This requires authentication and a running server
            # For now, we'll test the service directly
            service = BeemSMSService()
            
            # Test with a dummy number (won't actually send)
            result = service.send_sms(
                message=self.test_message,
                recipients=[self.test_phone],
                source_addr="TEST"
            )
            
            if result.get('success'):
                print("✅ SMS sending test successful!")
                print(f"   Provider: {result.get('provider')}")
                print(f"   Message count: {result.get('message_count')}")
                print(f"   Cost estimate: ${result.get('cost_estimate', 0)}")
            else:
                print("❌ SMS sending test failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
            return result.get('success', False)
        except BeemSMSError as e:
            print(f"❌ Beem SMS error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ SMS sending error: {str(e)}")
            return False
    
    def test_bulk_sms(self):
        """Test bulk SMS sending"""
        print("\n📤 Testing Bulk SMS Sending...")
        try:
            service = BeemSMSService()
            
            messages = [
                {
                    'message': f"Bulk test message 1 - {datetime.now().strftime('%H:%M:%S')}",
                    'recipients': [self.test_phone],
                    'recipient_ids': ['1']
                },
                {
                    'message': f"Bulk test message 2 - {datetime.now().strftime('%H:%M:%S')}",
                    'recipients': [self.test_phone],
                    'recipient_ids': ['2']
                }
            ]
            
            result = service.send_bulk_sms(messages)
            
            if result.get('success'):
                print("✅ Bulk SMS sending test successful!")
                print(f"   Provider: {result.get('provider')}")
                print(f"   Message count: {result.get('message_count')}")
                print(f"   Cost estimate: ${result.get('cost_estimate', 0)}")
            else:
                print("❌ Bulk SMS sending test failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
            return result.get('success', False)
        except BeemSMSError as e:
            print(f"❌ Beem bulk SMS error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Bulk SMS sending error: {str(e)}")
            return False
    
    def test_cost_calculation(self):
        """Test cost calculation"""
        print("\n💰 Testing Cost Calculation...")
        try:
            service = BeemSMSService()
            
            test_cases = [
                (1, 80),   # 1 recipient, 80 chars
                (1, 200),  # 1 recipient, 200 chars (2 SMS parts)
                (10, 80),  # 10 recipients, 80 chars
                (100, 160), # 100 recipients, 160 chars
            ]
            
            for recipients, message_length in test_cases:
                cost = service._calculate_cost(recipients, message_length)
                sms_parts = (message_length // 160) + 1
                print(f"   {recipients} recipients, {message_length} chars ({sms_parts} SMS parts) = ${cost:.4f}")
                
            return True
        except Exception as e:
            print(f"❌ Cost calculation error: {str(e)}")
            return False
    
    def test_environment_config(self):
        """Test environment configuration"""
        print("\n⚙️ Testing Environment Configuration...")
        
        required_settings = [
            'BEEM_API_KEY',
            'BEEM_SECRET_KEY',
            'BEEM_DEFAULT_SENDER_ID',
            'BEEM_API_TIMEOUT'
        ]
        
        all_configured = True
        for setting in required_settings:
            value = getattr(settings, setting, None)
            status = "✅" if value else "❌"
            print(f"   {status} {setting}: {'Configured' if value else 'Not configured'}")
            if not value:
                all_configured = False
        
        return all_configured
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Beem SMS Integration Tests")
        print("=" * 50)
        
        tests = [
            ("Environment Configuration", self.test_environment_config),
            ("Beem Connection", self.test_connection),
            ("Phone Validation", self.test_phone_validation),
            ("Cost Calculation", self.test_cost_calculation),
            ("SMS Sending", self.test_send_sms),
            ("Bulk SMS Sending", self.test_bulk_sms),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Beem SMS integration is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the configuration and try again.")
        
        return passed == total


def main():
    """Main function"""
    print("Mifumo WMS - Beem SMS Integration Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the Django project root directory")
        sys.exit(1)
    
    # Run tests
    tester = BeemSMSTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Configure your Beem API credentials in .env file")
        print("2. Run database migrations: python manage.py migrate")
        print("3. Start the development server: python manage.py runserver")
        print("4. Test the API endpoints using the provided documentation")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Beem API credentials are configured")
        print("2. Check that all required packages are installed")
        print("3. Verify database is properly set up")
        print("4. Check the logs for detailed error messages")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
