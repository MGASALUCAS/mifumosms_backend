#!/usr/bin/env python3
"""
Enhanced Webhook Handler for ZenoPay Payment Completion
This ensures SMS credits are properly added when payment is completed
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.utils import timezone
import logging
import json

from billing.models import PaymentTransaction, Purchase, SMSBalance
from billing.zenopay_service import ZenoPayService

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method="post",
    operation_description="Enhanced webhook endpoint for ZenoPay payment notifications with SMS credit addition.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "order_id": openapi.Schema(type=openapi.TYPE_STRING, description="ZenoPay order ID"),
            "payment_status": openapi.Schema(type=openapi.TYPE_STRING, description="Payment status"),
            "reference": openapi.Schema(type=openapi.TYPE_STRING, description="Payment reference"),
            "transid": openapi.Schema(type=openapi.TYPE_STRING, description="Transaction ID"),
            "channel": openapi.Schema(type=openapi.TYPE_STRING, description="Payment channel"),
            "msisdn": openapi.Schema(type=openapi.TYPE_STRING, description="Customer phone number"),
            "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Payment amount"),
            "currency": openapi.Schema(type=openapi.TYPE_STRING, description="Payment currency"),
            "data": openapi.Schema(type=openapi.TYPE_OBJECT, description="Additional payment data")
        }
    ),
    responses={
        200: openapi.Response(
            description="Webhook processed successfully",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Webhook processed successfully",
                    "data": {
                        "transaction_id": "uuid",
                        "payment_status": "COMPLETED",
                        "credits_added": 5000,
                        "new_balance": 5000
                    }
                }
            }
        ),
        400: openapi.Response(description="Bad request - invalid webhook data"),
        404: openapi.Response(description="Transaction not found"),
        500: openapi.Response(description="Internal server error")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Webhooks are external, no authentication required
def enhanced_payment_webhook(request):
    """
    Enhanced webhook handler for ZenoPay payment notifications.
    POST /api/billing/payments/webhook/
    
    This endpoint:
    1. Validates the webhook data
    2. Finds the payment transaction
    3. Updates payment status
    4. Completes the purchase
    5. Adds SMS credits to tenant balance
    6. Logs all actions for debugging
    """
    try:
        # Log incoming webhook
        webhook_data = request.data
        logger.info(f"Received ZenoPay webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Validate webhook data
        if not webhook_data:
            logger.error("Empty webhook data received")
            return Response({
                'success': False,
                'message': 'Empty webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract order ID
        order_id = webhook_data.get('order_id')
        if not order_id:
            logger.error("Missing order_id in webhook data")
            return Response({
                'success': False,
                'message': 'Missing order_id in webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process webhook with ZenoPay service
        zenopay_service = ZenoPayService()
        webhook_response = zenopay_service.process_webhook(webhook_data)
        
        if not webhook_response or not webhook_response.get('success'):
            logger.error(f"ZenoPay webhook processing failed: {webhook_response}")
            return Response({
                'success': False,
                'message': 'Webhook processing failed',
                'error': webhook_response.get('error', 'Unknown error') if webhook_response else 'No response from ZenoPay service'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract payment information
        payment_status = webhook_response.get('payment_status', '').upper()
        zenopay_order_id = webhook_response.get('order_id', order_id)
        
        logger.info(f"Processing payment status: {payment_status} for order: {zenopay_order_id}")
        
        # Find payment transaction
        try:
            payment_transaction = PaymentTransaction.objects.get(zenopay_order_id=zenopay_order_id)
            logger.info(f"Found payment transaction: {payment_transaction.id}")
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Payment transaction not found for zenopay_order_id: {zenopay_order_id}")
            return Response({
                'success': False,
                'message': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Process payment status
        with transaction.atomic():
            if payment_status == 'COMPLETED':
                logger.info(f"Processing completed payment for transaction: {payment_transaction.id}")
                
                # Update payment transaction
                payment_transaction.mark_as_completed(webhook_data)
                logger.info(f"Payment transaction marked as completed: {payment_transaction.id}")
                
                # Get associated purchase
                try:
                    purchase = payment_transaction.purchase
                    if not purchase:
                        logger.error(f"No associated purchase found for transaction: {payment_transaction.id}")
                        return Response({
                            'success': False,
                            'message': 'No associated purchase found'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    logger.info(f"Found associated purchase: {purchase.id}")
                    
                    # Complete purchase and add SMS credits
                    if purchase.complete_purchase():
                        logger.info(f"Purchase completed successfully: {purchase.id}")
                        logger.info(f"SMS credits added: {purchase.credits}")
                        
                        # Get updated balance
                        balance = SMSBalance.objects.get(tenant=payment_transaction.tenant)
                        logger.info(f"New SMS balance: {balance.credits}")
                        
                        # Log success
                        logger.info(f"SUCCESS: Payment completed and SMS credits added for tenant: {payment_transaction.tenant.name}")
                        
                        return Response({
                            'success': True,
                            'message': 'Webhook processed successfully',
                            'data': {
                                'transaction_id': str(payment_transaction.id),
                                'purchase_id': str(purchase.id),
                                'payment_status': payment_status,
                                'credits_added': purchase.credits,
                                'new_balance': balance.credits,
                                'tenant': payment_transaction.tenant.name,
                                'package': purchase.package.name
                            }
                        })
                    else:
                        logger.error(f"Failed to complete purchase: {purchase.id}")
                        return Response({
                            'success': False,
                            'message': 'Failed to complete purchase'
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except Exception as e:
                    logger.error(f"Error completing purchase: {str(e)}")
                    return Response({
                        'success': False,
                        'message': 'Error completing purchase',
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            elif payment_status == 'FAILED':
                logger.info(f"Processing failed payment for transaction: {payment_transaction.id}")
                
                # Mark payment as failed
                payment_transaction.mark_as_failed('Payment failed via webhook')
                
                # Mark purchase as failed
                if hasattr(payment_transaction, 'purchase') and payment_transaction.purchase:
                    payment_transaction.purchase.mark_as_failed()
                    logger.info(f"Purchase marked as failed: {payment_transaction.purchase.id}")
                
                logger.info(f"Payment transaction marked as failed: {payment_transaction.id}")
                
                return Response({
                    'success': True,
                    'message': 'Payment failure processed successfully',
                    'data': {
                        'transaction_id': str(payment_transaction.id),
                        'payment_status': payment_status,
                        'status': 'failed'
                    }
                })
                
            else:
                # Other statuses (PENDING, PROCESSING, etc.)
                logger.info(f"Processing {payment_status} payment for transaction: {payment_transaction.id}")
                
                # Update webhook data but don't change status
                payment_transaction.webhook_data = webhook_data
                payment_transaction.save()
                
                logger.info(f"Payment transaction updated with webhook data: {payment_transaction.id}")
                
                return Response({
                    'success': True,
                    'message': 'Webhook data updated successfully',
                    'data': {
                        'transaction_id': str(payment_transaction.id),
                        'payment_status': payment_status,
                        'status': payment_transaction.status
                    }
                })
                
    except Exception as e:
        logger.exception(f"Webhook processing error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Webhook processing failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_webhook_processing():
    """Test webhook processing with sample data."""
    print("Testing Enhanced Webhook Processing")
    print("=" * 50)
    
    # Get a test payment transaction
    payment_transaction = PaymentTransaction.objects.filter(status='processing').first()
    
    if not payment_transaction:
        print("No processing payment transactions found for testing")
        return
    
    print(f"Testing with transaction: {payment_transaction.id}")
    print(f"Order ID: {payment_transaction.zenopay_order_id}")
    print(f"Amount: {payment_transaction.amount} {payment_transaction.currency}")
    print(f"Tenant: {payment_transaction.tenant.name}")
    
    # Simulate webhook data
    webhook_data = {
        'order_id': payment_transaction.zenopay_order_id,
        'payment_status': 'COMPLETED',
        'reference': f'REF-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        'transid': f'TXN-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        'channel': f'{payment_transaction.mobile_money_provider.upper()}-TZ',
        'msisdn': payment_transaction.buyer_phone,
        'amount': float(payment_transaction.amount),
        'currency': payment_transaction.currency,
        'data': {
            'timestamp': timezone.now().isoformat(),
            'provider': payment_transaction.mobile_money_provider
        }
    }
    
    print(f"\nSimulating webhook data:")
    print(f"  Order ID: {webhook_data['order_id']}")
    print(f"  Status: {webhook_data['payment_status']}")
    print(f"  Reference: {webhook_data['reference']}")
    print(f"  Channel: {webhook_data['channel']}")
    
    # Get initial balance
    initial_balance = SMSBalance.objects.get(tenant=payment_transaction.tenant).credits
    print(f"\nInitial SMS balance: {initial_balance}")
    
    # Process webhook
    print(f"\nProcessing webhook...")
    # Note: In real implementation, this would be called by Django's request handling
    # For testing, we'll simulate the webhook processing logic
    
    try:
        # Update payment transaction
        payment_transaction.mark_as_completed(webhook_data)
        print(f"✅ Payment transaction marked as completed")
        
        # Complete purchase
        if hasattr(payment_transaction, 'purchase') and payment_transaction.purchase:
            purchase = payment_transaction.purchase
            if purchase.complete_purchase():
                print(f"✅ Purchase completed successfully")
                print(f"✅ SMS credits added: {purchase.credits}")
                
                # Get updated balance
                updated_balance = SMSBalance.objects.get(tenant=payment_transaction.tenant).credits
                print(f"✅ New SMS balance: {updated_balance}")
                print(f"✅ Credits added: {updated_balance - initial_balance}")
                
                print(f"\nSUCCESS: Webhook processing completed successfully!")
            else:
                print(f"❌ Failed to complete purchase")
        else:
            print(f"❌ No associated purchase found")
            
    except Exception as e:
        print(f"❌ Webhook processing failed: {str(e)}")

if __name__ == "__main__":
    # This would be run as a standalone script for testing
    import os
    import sys
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
    django.setup()
    
    test_webhook_processing()
