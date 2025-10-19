#!/usr/bin/env python
"""
Simple billing API test runner without emojis for Windows compatibility.
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

def setup_test_environment():
    """Set up the test environment."""
    print("Setting up test environment...")
    
    # Set up Django
    django.setup()
    
    # Configure test settings
    settings.DEBUG = True
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    
    print("Test environment ready!")

def run_all_tests():
    """Run all billing API tests."""
    print("\nRunning Complete Billing API Test Suite...")
    print("=" * 60)
    
    setup_test_environment()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    # Run all billing tests
    test_modules = [
        'billing.tests',
        'billing.integration_tests'
    ]
    
    total_failures = 0
    for test_module in test_modules:
        print(f"\nRunning {test_module}...")
        failures = test_runner.run_tests([test_module])
        total_failures += failures
        
        if failures:
            print(f"FAILED: {test_module} had {failures} failure(s)")
        else:
            print(f"PASSED: {test_module}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if total_failures == 0:
        print("SUCCESS: All tests passed!")
        print("- API responses match documentation")
        print("- All endpoints are functional")
        print("- Data consistency verified")
        print("- Error handling works properly")
        print("- Authentication and authorization work")
        return True
    else:
        print(f"FAILED: {total_failures} test(s) failed")
        print("Check the test output above for specific issues")
        return False

def run_unit_tests_only():
    """Run only unit tests."""
    print("\nRunning Unit Tests Only...")
    print("=" * 50)
    
    setup_test_environment()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    failures = test_runner.run_tests(['billing.tests'])
    
    if failures:
        print(f"FAILED: Unit tests had {failures} failure(s)")
        return False
    else:
        print("PASSED: All unit tests passed!")
        return True

def run_integration_tests_only():
    """Run only integration tests."""
    print("\nRunning Integration Tests Only...")
    print("=" * 50)
    
    setup_test_environment()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    failures = test_runner.run_tests(['billing.integration_tests'])
    
    if failures:
        print(f"FAILED: Integration tests had {failures} failure(s)")
        return False
    else:
        print("PASSED: All integration tests passed!")
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Billing API Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    
    args = parser.parse_args()
    
    try:
        if args.unit:
            success = run_unit_tests_only()
        elif args.integration:
            success = run_integration_tests_only()
        else:
            success = run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
