#!/usr/bin/env python3
"""
Test the working BeemSMSService directly to see if it actually works
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.beem_sms import BeemSMSService

def test_working_beem_direct():
    """Test the working BeemSMSService directly."""
    print("=" * 80)
    print("TESTING WORKING BEEM SMS SERVICE DIRECTLY")
    print("=" * 80)
    
    try:
        # Initialize BeemSMS service
        beem_service = BeemSMSService()
        print("BeemSMS service initialized successfully")
        
        # Test sending SMS with Taarifa-SMS (the working sender ID)
        print("\nTesting with Taarifa-SMS sender ID...")
        
        result = beem_service.send_sms(
            message="Test message from working BeemSMS service",
            recipients=["255700000001"],
            source_addr="Taarifa-SMS",
            recipient_ids=["test_working_direct"]
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Taarifa-SMS works!")
        else:
            print("FAILED: Taarifa-SMS failed")
            
    except Exception as e:
        print(f"BeemSMS service error: {e}")
        import traceback
        traceback.print_exc()

def test_quantum_sender():
    """Test with Quantum sender ID."""
    print("\n" + "=" * 80)
    print("TESTING WITH QUANTUM SENDER ID")
    print("=" * 80)
    
    try:
        beem_service = BeemSMSService()
        
        result = beem_service.send_sms(
            message="Test message with Quantum sender ID",
            recipients=["255700000001"],
            source_addr="Quantum",
            recipient_ids=["test_quantum"]
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Quantum works!")
        else:
            print("FAILED: Quantum failed")
            
    except Exception as e:
        print(f"Quantum test error: {e}")

def main():
    """Run all tests."""
    print("Testing Working BeemSMS Service Directly")
    print("=" * 80)
    
    test_working_beem_direct()
    test_quantum_sender()

if __name__ == "__main__":
    main()
