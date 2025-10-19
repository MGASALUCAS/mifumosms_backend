#!/usr/bin/env python
"""
Test runner for billing API tests.
Run this script to execute all billing API tests with real data validation.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')

def run_tests():
    """Run the billing API tests."""
    print("🚀 Starting Billing API Tests...")
    print("=" * 50)
    
    # Set up Django
    django.setup()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Run tests
    failures = test_runner.run_tests(['billing.tests'])
    
    print("=" * 50)
    if failures:
        print(f"❌ Tests failed with {failures} failure(s)")
        return False
    else:
        print("✅ All tests passed successfully!")
        return True

def run_specific_test(test_class=None, test_method=None):
    """Run specific test class or method."""
    print(f"🧪 Running specific test: {test_class}.{test_method if test_method else 'all'}")
    print("=" * 50)
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    if test_class and test_method:
        test_path = f'billing.tests.{test_class}.{test_method}'
    elif test_class:
        test_path = f'billing.tests.{test_class}'
    else:
        test_path = 'billing.tests'
    
    failures = test_runner.run_tests([test_path])
    
    print("=" * 50)
    if failures:
        print(f"❌ Test failed with {failures} failure(s)")
        return False
    else:
        print("✅ Test passed successfully!")
        return True

def run_api_validation_tests():
    """Run tests that validate API responses against documentation."""
    print("📋 Running API Documentation Validation Tests...")
    print("=" * 50)
    
    # Test classes that validate API responses
    validation_tests = [
        'SMSPackageAPITests',
        'SMSBalanceAPITests', 
        'UsageStatisticsAPITests',
        'PurchaseAPITests',
        'PaymentAPITests',
        'CustomSMSAPITests',
        'SubscriptionAPITests'
    ]
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    all_passed = True
    for test_class in validation_tests:
        print(f"\n🔍 Testing {test_class}...")
        failures = test_runner.run_tests([f'billing.tests.{test_class}'])
        if failures:
            all_passed = False
            print(f"❌ {test_class} failed with {failures} failure(s)")
        else:
            print(f"✅ {test_class} passed")
    
    print("=" * 50)
    if all_passed:
        print("✅ All API validation tests passed!")
    else:
        print("❌ Some API validation tests failed!")
    
    return all_passed

def run_integration_tests():
    """Run integration tests that test complete workflows."""
    print("🔗 Running Integration Tests...")
    print("=" * 50)
    
    # Integration test scenarios
    integration_tests = [
        'test_complete_payment_flow',
        'test_sms_package_purchase_workflow',
        'test_custom_sms_purchase_workflow',
        'test_subscription_management_workflow'
    ]
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    all_passed = True
    for test_method in integration_tests:
        print(f"\n🔗 Testing {test_method}...")
        failures = test_runner.run_tests([f'billing.tests.PaymentAPITests.{test_method}'])
        if failures:
            all_passed = False
            print(f"❌ {test_method} failed with {failures} failure(s)")
        else:
            print(f"✅ {test_method} passed")
    
    print("=" * 50)
    if all_passed:
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed!")
    
    return all_passed

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Billing API Tests')
    parser.add_argument('--test-class', help='Run specific test class')
    parser.add_argument('--test-method', help='Run specific test method')
    parser.add_argument('--validation-only', action='store_true', help='Run only API validation tests')
    parser.add_argument('--integration-only', action='store_true', help='Run only integration tests')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    if args.validation_only:
        success = run_api_validation_tests()
    elif args.integration_only:
        success = run_integration_tests()
    elif args.test_class:
        success = run_specific_test(args.test_class, args.test_method)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)
