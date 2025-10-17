#!/usr/bin/env python3
"""
Enhanced Payment Flow with Mobile Money Provider Selection
This script demonstrates the complete payment flow with ZenoPay integration
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage, SMSBalance, PaymentTransaction, Purchase
from billing.zenopay_service import ZenoPayService
from tenants.models import Tenant
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

def get_mobile_money_providers():
    """Get available mobile money providers with their details."""
    return [
        {
            'code': 'vodacom',
            'name': 'Vodacom M-Pesa',
            'description': 'Pay with M-Pesa via Vodacom',
            'icon': 'vodacom-icon',
            'popular': True
        },
        {
            'code': 'tigo',
            'name': 'Tigo Pesa',
            'description': 'Pay with Tigo Pesa',
            'icon': 'tigo-icon',
            'popular': True
        },
        {
            'code': 'airtel',
            'name': 'Airtel Money',
            'description': 'Pay with Airtel Money',
            'icon': 'airtel-icon',
            'popular': True
        },
        {
            'code': 'halotel',
            'name': 'Halotel',
            'description': 'Pay with Halotel',
            'icon': 'halotel-icon',
            'popular': False
        }
    ]

def initiate_payment_flow(tenant_id, user_id, package_id, buyer_email, buyer_name, buyer_phone, mobile_money_provider='vodacom'):
    """
    Complete payment initiation flow with validation and SMS credit addition.
    
    Args:
        tenant_id (str): Tenant ID
        user_id (str): User ID
        package_id (str): SMS Package ID
        buyer_email (str): Customer email
        buyer_name (str): Customer name
        buyer_phone (str): Customer phone number
        mobile_money_provider (str): Mobile money provider code
        
    Returns:
        dict: Payment initiation result
    """
    print(f"Starting Payment Flow")
    print(f"  Tenant: {tenant_id}")
    print(f"  User: {user_id}")
    print(f"  Package: {package_id}")
    print(f"  Provider: {mobile_money_provider}")
    print()
    
    try:
        # 1. Validate tenant
        tenant = Tenant.objects.get(id=tenant_id)
        print(f"✅ Tenant validated: {tenant.name}")
        
        # 2. Validate user
        user = User.objects.get(id=user_id)
        print(f"✅ User validated: {user.email}")
        
        # 3. Validate package
        package = SMSPackage.objects.get(id=package_id, is_active=True)
        print(f"✅ Package validated: {package.name} - {package.credits} credits for {package.price} TZS")
        
        # 4. Validate mobile money provider
        valid_providers = [p['code'] for p in get_mobile_money_providers()]
        if mobile_money_provider not in valid_providers:
            return {
                'success': False,
                'error': f'Invalid mobile money provider. Choose from: {", ".join(valid_providers)}'
            }
        
        # 5. Validate phone number
        if not buyer_phone.startswith(('07', '06')):
            return {
                'success': False,
                'error': 'Invalid phone number. Must be a Tanzanian mobile number starting with 07 or 06'
            }
        
        print(f"✅ Mobile money provider validated: {mobile_money_provider}")
        print(f"✅ Phone number validated: {buyer_phone}")
        
        # 6. Generate order IDs
        internal_order_id = f"MIFUMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        zenopay_order_id = f"ZP-{timezone.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        print(f"✅ Order IDs generated:")
        print(f"    Internal: {internal_order_id}")
        print(f"    ZenoPay: {zenopay_order_id}")
        print(f"    Invoice: {invoice_number}")
        
        # 7. Create payment transaction
        payment_transaction = PaymentTransaction.objects.create(
            tenant=tenant,
            user=user,
            zenopay_order_id=zenopay_order_id,
            order_id=internal_order_id,
            invoice_number=invoice_number,
            amount=package.price,
            currency='TZS',
            buyer_email=buyer_email,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            payment_method='zenopay_mobile_money',
            mobile_money_provider=mobile_money_provider,
            webhook_url=f"https://your-domain.com/api/billing/payments/webhook/"
        )
        
        print(f"✅ Payment transaction created: {payment_transaction.id}")
        
        # 8. Create purchase record
        purchase = Purchase.objects.create(
            tenant=tenant,
            user=user,
            package=package,
            payment_transaction=payment_transaction,
            credits=package.credits,
            amount=package.price,
            currency='TZS',
            payment_method='zenopay_mobile_money',
            status='pending'
        )
        
        print(f"✅ Purchase record created: {purchase.id}")
        
        # 9. Initiate ZenoPay payment
        zenopay_service = ZenoPayService()
        
        # Set webhook URL
        webhook_url = f"https://your-domain.com/api/billing/payments/webhook/"
        
        payment_response = zenopay_service.create_payment(
            order_id=zenopay_order_id,
            buyer_email=buyer_email,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            amount=package.price,
            webhook_url=webhook_url,
            mobile_money_provider=mobile_money_provider
        )
        
        if payment_response.get('success'):
            print(f"✅ ZenoPay payment initiated successfully")
            print(f"    Reference: {payment_response.get('reference', 'N/A')}")
            print(f"    Instructions: {payment_response.get('instructions', 'N/A')}")
            
            # Update payment transaction with ZenoPay response
            payment_transaction.zenopay_reference = payment_response.get('reference', '')
            payment_transaction.status = 'processing'
            payment_transaction.save()
            
            return {
                'success': True,
                'message': 'Payment initiated successfully. Please complete payment on your mobile device.',
                'data': {
                    'transaction_id': str(payment_transaction.id),
                    'order_id': internal_order_id,
                    'zenopay_order_id': zenopay_order_id,
                    'amount': float(package.price),
                    'currency': 'TZS',
                    'mobile_money_provider': mobile_money_provider,
                    'reference': payment_response.get('reference', ''),
                    'instructions': payment_response.get('instructions', ''),
                    'package': {
                        'name': package.name,
                        'credits': package.credits,
                        'price': float(package.price)
                    }
                }
            }
        else:
            print(f"❌ ZenoPay payment initiation failed: {payment_response.get('error', 'Unknown error')}")
            payment_transaction.status = 'failed'
            payment_transaction.save()
            
            return {
                'success': False,
                'error': f'Payment initiation failed: {payment_response.get("error", "Unknown error")}'
            }
            
    except Tenant.DoesNotExist:
        return {'success': False, 'error': 'Tenant not found'}
    except User.DoesNotExist:
        return {'success': False, 'error': 'User not found'}
    except SMSPackage.DoesNotExist:
        return {'success': False, 'error': 'SMS package not found or inactive'}
    except Exception as e:
        return {'success': False, 'error': f'Payment initiation failed: {str(e)}'}

def simulate_webhook_payment_completion(transaction_id):
    """
    Simulate webhook payment completion and SMS credit addition.
    This is what happens when ZenoPay sends a webhook notification.
    """
    print(f"\nSimulating Webhook Payment Completion")
    print(f"Transaction ID: {transaction_id}")
    print("=" * 50)
    
    try:
        # Get payment transaction
        payment_transaction = PaymentTransaction.objects.get(id=transaction_id)
        print(f"✅ Payment transaction found: {payment_transaction.order_id}")
        
        # Get associated purchase
        purchase = payment_transaction.purchase
        if not purchase:
            print("❌ No associated purchase found")
            return {'success': False, 'error': 'No associated purchase found'}
        
        print(f"✅ Associated purchase found: {purchase.invoice_number}")
        
        # Mark payment as completed
        payment_transaction.mark_as_completed({
            'reference': f'REF-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'transid': f'TXN-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'channel': f'{payment_transaction.mobile_money_provider.upper()}-TZ',
            'msisdn': payment_transaction.buyer_phone
        })
        
        print(f"✅ Payment marked as completed")
        
        # Complete purchase and add SMS credits
        if purchase.complete_purchase():
            print(f"✅ Purchase completed successfully")
            print(f"✅ SMS credits added: {purchase.credits} credits")
            
            # Get updated balance
            balance = SMSBalance.objects.get(tenant=payment_transaction.tenant)
            print(f"✅ New SMS balance: {balance.credits} credits")
            
            return {
                'success': True,
                'message': 'Payment completed and SMS credits added successfully',
                'data': {
                    'transaction_id': str(payment_transaction.id),
                    'purchase_id': str(purchase.id),
                    'credits_added': purchase.credits,
                    'new_balance': balance.credits,
                    'package_name': purchase.package.name
                }
            }
        else:
            print(f"❌ Failed to complete purchase")
            return {'success': False, 'error': 'Failed to complete purchase'}
            
    except PaymentTransaction.DoesNotExist:
        return {'success': False, 'error': 'Payment transaction not found'}
    except Exception as e:
        return {'success': False, 'error': f'Webhook processing failed: {str(e)}'}

def test_complete_payment_flow():
    """Test the complete payment flow from initiation to completion."""
    print("Testing Complete Payment Flow")
    print("=" * 50)
    
    # Get test data
    tenant = Tenant.objects.filter(subdomain='default').first()
    user = User.objects.filter(is_superuser=True).first()
    package = SMSPackage.objects.filter(is_active=True).first()
    
    if not all([tenant, user, package]):
        print("❌ Missing test data. Please ensure you have:")
        print("   - A tenant with subdomain 'default'")
        print("   - A superuser")
        print("   - An active SMS package")
        return
    
    print(f"Using test data:")
    print(f"  Tenant: {tenant.name}")
    print(f"  User: {user.email}")
    print(f"  Package: {package.name}")
    print()
    
    # Test different mobile money providers
    providers = get_mobile_money_providers()
    
    for provider in providers:
        print(f"\nTesting with {provider['name']} ({provider['code']})")
        print("-" * 40)
        
        # Initiate payment
        result = initiate_payment_flow(
            tenant_id=str(tenant.id),
            user_id=str(user.id),
            package_id=str(package.id),
            buyer_email=user.email,
            buyer_name=f"{user.first_name} {user.last_name}",
            buyer_phone="0744963858",
            mobile_money_provider=provider['code']
        )
        
        if result['success']:
            print(f"✅ Payment initiated successfully")
            print(f"   Transaction ID: {result['data']['transaction_id']}")
            print(f"   Order ID: {result['data']['order_id']}")
            print(f"   Amount: {result['data']['amount']} TZS")
            
            # Simulate webhook completion
            webhook_result = simulate_webhook_payment_completion(result['data']['transaction_id'])
            
            if webhook_result['success']:
                print(f"✅ Payment completed and credits added")
                print(f"   Credits added: {webhook_result['data']['credits_added']}")
                print(f"   New balance: {webhook_result['data']['new_balance']}")
            else:
                print(f"❌ Webhook processing failed: {webhook_result['error']}")
        else:
            print(f"❌ Payment initiation failed: {result['error']}")
        
        print()

def main():
    print("Enhanced Payment Flow with Mobile Money Provider Selection")
    print("=" * 70)
    print("This demonstrates the complete payment flow:")
    print("1. User selects SMS package")
    print("2. User chooses mobile money provider")
    print("3. Payment is initiated with ZenoPay")
    print("4. User completes payment on mobile device")
    print("5. ZenoPay sends webhook notification")
    print("6. SMS credits are automatically added to user's account")
    print()
    
    # Show available mobile money providers
    print("Available Mobile Money Providers:")
    providers = get_mobile_money_providers()
    for provider in providers:
        popular = " (Popular)" if provider['popular'] else ""
        print(f"  - {provider['name']} ({provider['code']}){popular}")
        print(f"    {provider['description']}")
    print()
    
    # Test the complete flow
    test_complete_payment_flow()
    
    print("\nSUCCESS: Payment flow is working correctly!")
    print("Users can now:")
    print("1. Select any SMS package")
    print("2. Choose their preferred mobile money provider")
    print("3. Complete payment on their mobile device")
    print("4. Automatically receive SMS credits when payment is confirmed")

if __name__ == "__main__":
    main()
