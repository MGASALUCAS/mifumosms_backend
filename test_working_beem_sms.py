#!/usr/bin/env python3
"""
Test the working BeemSMS service directly
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

def test_working_beem_sms():
    """Test the working BeemSMS service directly."""
    print("=" * 80)
    print("TESTING WORKING BEEM SMS SERVICE")
    print("=" * 80)
    
    try:
        # Initialize BeemSMS service
        beem_service = BeemSMSService()
        print("BeemSMS service initialized successfully")
        
        # Test sending SMS with different sender IDs
        sender_ids_to_test = ["Quantum", "Taarifa-SMS", "INFO", "MIFUMO"]
        
        for sender_id in sender_ids_to_test:
            print(f"\nTesting with sender ID: {sender_id}")
            
            try:
                result = beem_service.send_sms(
                    message=f"Test message with {sender_id}",
                    recipients=["255700000001"],
                    source_addr=sender_id,
                    recipient_ids=["test_1"]
                )
                
                print(f"Result: {result}")
                
                if result.get('success'):
                    print(f"SUCCESS: {sender_id} works!")
                    break
                else:
                    print(f"FAILED: {sender_id}")
                    
            except Exception as e:
                print(f"ERROR with {sender_id}: {e}")
                
    except Exception as e:
        print(f"BeemSMS service initialization error: {e}")
        import traceback
        traceback.print_exc()

def test_balance_check():
    """Test balance check to verify API credentials."""
    print("\n" + "=" * 80)
    print("TESTING BALANCE CHECK")
    print("=" * 80)
    
    try:
        beem_service = BeemSMSService()
        balance_result = beem_service.check_balance()
        print(f"Balance check result: {balance_result}")
        
    except Exception as e:
        print(f"Balance check error: {e}")

def test_sender_names():
    """Test getting sender names."""
    print("\n" + "=" * 80)
    print("TESTING SENDER NAMES")
    print("=" * 80)
    
    try:
        beem_service = BeemSMSService()
        sender_names = beem_service.get_sender_names()
        print(f"Sender names result: {sender_names}")
        
    except Exception as e:
        print(f"Sender names error: {e}")

def main():
    """Run all tests."""
    print("Testing Working BeemSMS Service")
    print("=" * 80)
    
    test_balance_check()
    test_sender_names()
    test_working_beem_sms()

if __name__ == "__main__":
    main()
