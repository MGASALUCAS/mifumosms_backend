#!/usr/bin/env python
"""
Simple test runner for billing API tests.
"""
import os
import sys
import subprocess

def main():
    """Run the billing API tests."""
    print("🚀 Running Billing API Tests...")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    try:
        # Run the test suite
        result = subprocess.run([
            sys.executable, 'test_billing_api.py'
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print("\n✅ All tests completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print("❌ Tests failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return e.returncode
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
