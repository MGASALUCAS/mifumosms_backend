#!/usr/bin/env python3
"""
Enhanced Payment Endpoints with Mobile Money Provider Selection
This file contains the enhanced payment API endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import uuid
import logging

from billing.models import SMSPackage, PaymentTransaction, Purchase, SMSBalance
from billing.zenopay_service import ZenoPayService
from billing.serializers import PaymentTransactionSerializer

logger = logging.getLogger(__name__)

def get_mobile_money_providers():
    """Get available mobile money providers with their details."""
    return [
        {
            'code': 'vodacom',
            'name': 'Vodacom M-Pesa',
            'description': 'Pay with M-Pesa via Vodacom',
            'icon': 'vodacom-icon',
            'popular': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'tigo',
            'name': 'Tigo Pesa',
            'description': 'Pay with Tigo Pesa',
            'icon': 'tigo-icon',
            'popular': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'airtel',
            'name': 'Airtel Money',
            'description': 'Pay with Airtel Money',
            'icon': 'airtel-icon',
            'popular': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'halotel',
            'name': 'Halotel',
            'description': 'Pay with Halotel',
            'icon': 'halotel-icon',
            'popular': False,
            'min_amount': 1000,
            'max_amount': 500000
        }
    ]

@swagger_auto_schema(
    method="get",
    operation_description="Get available mobile money providers for payment.",
    responses={
        200: openapi.Response(
            description="List of available mobile money providers",
            examples={
                "application/json": {
                    "success": True,
                    "data": [
                        {
                            "code": "vodacom",
                            "name": "Vodacom M-Pesa",
                            "description": "Pay with M-Pesa via Vodacom",
                            "icon": "vodacom-icon",
                            "popular": True,
                            "min_amount": 1000,
                            "max_amount": 1000000
                        }
                    ]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mobile_money_providers_endpoint(request):
    """
    Get available mobile money providers for payment.
    GET /api/billing/payments/providers/
    """
    try:
        providers = get_mobile_money_providers()
        
        return Response({
            'success': True,
            'data': providers,
            'message': f'Found {len(providers)} mobile money providers'
        })
        
    except Exception as e:
        logger.error(f"Error getting mobile money providers: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get mobile money providers',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method="post",
    operation_description="Initiate payment with ZenoPay for an SMS package with mobile money provider selection.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["package_id", "buyer_email", "buyer_name", "buyer_phone", "mobile_money_provider"],
        properties={
            "package_id": openapi.Schema(
                type=openapi.TYPE_STRING, 
                format=openapi.FORMAT_UUID,
                description="SMS Package ID"
            ),
            "buyer_email": openapi.Schema(
                type=openapi.TYPE_STRING, 
                format=openapi.FORMAT_EMAIL,
                description="Customer email address"
            ),
            "buyer_name": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Customer full name"
            ),
            "buyer_phone": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Customer phone number (07XXXXXXXX or 06XXXXXXXX)"
            ),
            "mobile_money_provider": openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=["vodacom", "tigo", "airtel", "halotel"],
                description="Mobile money provider code"
            )
        }
    ),
    responses={
        201: openapi.Response(
            description="Payment initiated successfully",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Payment initiated successfully. Please complete payment on your mobile device.",
                    "data": {
                        "transaction_id": "uuid",
                        "order_id": "MIFUMO-20241017-ABC12345",
                        "zenopay_order_id": "ZP-20241017123456-ABC12345",
                        "amount": 150000.00,
                        "currency": "TZS",
                        "mobile_money_provider": "vodacom",
                        "reference": "REF123456789",
                        "instructions": "Please complete payment on your mobile device",
                        "package": {
                            "name": "Lite",
                            "credits": 5000,
                            "price": 150000.00
                        }
                    }
                }
            }
        ),
        400: openapi.Response(description="Bad request - validation errors"),
        404: openapi.Response(description="Package not found")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment_enhanced(request):
    """
    Initiate payment with ZenoPay for SMS package purchase with mobile money provider selection.
    POST /api/billing/payments/initiate/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract and validate request data
        package_id = request.data.get('package_id')
        buyer_email = request.data.get('buyer_email')
        buyer_name = request.data.get('buyer_name')
        buyer_phone = request.data.get('buyer_phone')
        mobile_money_provider = request.data.get('mobile_money_provider', 'vodacom')

        # Validate required fields
        if not all([package_id, buyer_email, buyer_name, buyer_phone]):
            return Response({
                'success': False,
                'message': 'Missing required fields: package_id, buyer_email, buyer_name, buyer_phone'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate mobile money provider
        valid_providers = [p['code'] for p in get_mobile_money_providers()]
        if mobile_money_provider not in valid_providers:
            return Response({
                'success': False,
                'message': f'Invalid mobile money provider. Choose from: {", ".join(valid_providers)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate phone number format
        if not buyer_phone.startswith(('07', '06')):
            return Response({
                'success': False,
                'message': 'Invalid phone number. Must be a Tanzanian mobile number starting with 07 or 06 (e.g., 0744963858)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate package_id format
        try:
            uuid.UUID(package_id)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'message': f'Invalid package ID format: {package_id}. Please select a valid package.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get and validate package
        try:
            package = SMSPackage.objects.get(id=package_id, is_active=True)
        except SMSPackage.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Package not found or inactive. Please select a valid package.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if package amount is within provider limits
        provider_info = next((p for p in get_mobile_money_providers() if p['code'] == mobile_money_provider), None)
        if provider_info:
            if package.price < provider_info['min_amount']:
                return Response({
                    'success': False,
                    'message': f'Package amount ({package.price} TZS) is below minimum for {provider_info["name"]} ({provider_info["min_amount"]} TZS)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if package.price > provider_info['max_amount']:
                return Response({
                    'success': False,
                    'message': f'Package amount ({package.price} TZS) exceeds maximum for {provider_info["name"]} ({provider_info["max_amount"]} TZS)'
                }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Generate unique IDs
            internal_order_id = f"MIFUMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            zenopay_order_id = f"ZP-{timezone.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            # Set webhook URL
            base_url = getattr(settings, "BASE_URL", "").rstrip("/")
            webhook_url = f"{base_url}/api/billing/payments/webhook/" if base_url else "/api/billing/payments/webhook/"

            # Create payment transaction
            payment_transaction = PaymentTransaction.objects.create(
                tenant=tenant,
                user=request.user,
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
                webhook_url=webhook_url
            )

            # Create purchase record
            purchase = Purchase.objects.create(
                tenant=tenant,
                user=request.user,
                package=package,
                payment_transaction=payment_transaction,
                credits=package.credits,
                amount=package.price,
                currency='TZS',
                payment_method='zenopay_mobile_money',
                status='pending'
            )

            # Initiate ZenoPay payment
            zenopay_service = ZenoPayService()
            
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
                # Update payment transaction with ZenoPay response
                payment_transaction.zenopay_reference = payment_response.get('reference', '')
                payment_transaction.status = 'processing'
                payment_transaction.save()

                # Serialize response
                serializer = PaymentTransactionSerializer(payment_transaction)
                
                return Response({
                    'success': True,
                    'message': 'Payment initiated successfully. Please complete payment on your mobile device.',
                    'data': {
                        'transaction_id': str(payment_transaction.id),
                        'order_id': internal_order_id,
                        'zenopay_order_id': zenopay_order_id,
                        'amount': float(package.price),
                        'currency': 'TZS',
                        'mobile_money_provider': mobile_money_provider,
                        'provider_name': provider_info['name'] if provider_info else mobile_money_provider,
                        'reference': payment_response.get('reference', ''),
                        'instructions': payment_response.get('instructions', 'Please complete payment on your mobile device'),
                        'package': {
                            'id': str(package.id),
                            'name': package.name,
                            'credits': package.credits,
                            'price': float(package.price),
                            'unit_price': float(package.unit_price)
                        },
                        'buyer': {
                            'name': buyer_name,
                            'email': buyer_email,
                            'phone': buyer_phone
                        }
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # Mark transaction as failed
                payment_transaction.status = 'failed'
                payment_transaction.save()
                
                return Response({
                    'success': False,
                    'message': f'Payment initiation failed: {payment_response.get("error", "Unknown error")}'
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Payment initiation failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method="get",
    operation_description="Get payment status and progress for a transaction.",
    manual_parameters=[
        openapi.Parameter(
            'transaction_id',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description="Payment Transaction UUID",
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Payment status retrieved successfully",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "transaction_id": "uuid",
                        "order_id": "MIFUMO-20241017-ABC12345",
                        "status": "processing",
                        "payment_status": "PENDING",
                        "amount": 150000.00,
                        "reference": "REF123456789",
                        "progress": {
                            "step": 2,
                            "total_steps": 4,
                            "current_step": "Payment Pending",
                            "description": "Please complete payment on your mobile device"
                        },
                        "updated_at": "2024-10-17T12:34:56Z"
                    }
                }
            }
        ),
        404: openapi.Response(description="Transaction not found")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status_enhanced(request, transaction_id):
    """
    Get payment status and progress for a transaction.
    GET /api/billing/payments/status/{transaction_id}/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_transaction = PaymentTransaction.objects.get(
                id=transaction_id,
                tenant=tenant
            )
        except PaymentTransaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get payment progress
        progress = _get_payment_progress_enhanced(payment_transaction)

        return Response({
            'success': True,
            'data': {
                'transaction_id': str(payment_transaction.id),
                'order_id': payment_transaction.order_id,
                'zenopay_order_id': payment_transaction.zenopay_order_id,
                'status': payment_transaction.status,
                'amount': float(payment_transaction.amount),
                'currency': payment_transaction.currency,
                'mobile_money_provider': payment_transaction.mobile_money_provider,
                'reference': payment_transaction.zenopay_reference,
                'buyer': {
                    'name': payment_transaction.buyer_name,
                    'email': payment_transaction.buyer_email,
                    'phone': payment_transaction.buyer_phone
                },
                'progress': progress,
                'created_at': payment_transaction.created_at.isoformat(),
                'updated_at': payment_transaction.updated_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to get payment status',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_payment_progress_enhanced(payment_transaction):
    """Get enhanced payment progress information."""
    status_mapping = {
        'pending': {
            'step': 1,
            'total_steps': 4,
            'current_step': 'Payment Initiated',
            'description': 'Payment request has been created and is being processed',
            'icon': 'clock',
            'color': 'blue'
        },
        'processing': {
            'step': 2,
            'total_steps': 4,
            'current_step': 'Payment Pending',
            'description': 'Please complete payment on your mobile device',
            'icon': 'mobile',
            'color': 'orange'
        },
        'completed': {
            'step': 4,
            'total_steps': 4,
            'current_step': 'Payment Completed',
            'description': 'Payment successful! SMS credits have been added to your account',
            'icon': 'check-circle',
            'color': 'green'
        },
        'failed': {
            'step': 0,
            'total_steps': 4,
            'current_step': 'Payment Failed',
            'description': 'Payment failed. Please try again or contact support',
            'icon': 'x-circle',
            'color': 'red'
        },
        'cancelled': {
            'step': 0,
            'total_steps': 4,
            'current_step': 'Payment Cancelled',
            'description': 'Payment was cancelled',
            'icon': 'x-circle',
            'color': 'gray'
        },
        'expired': {
            'step': 0,
            'total_steps': 4,
            'current_step': 'Payment Expired',
            'description': 'Payment has expired. Please initiate a new payment',
            'icon': 'clock',
            'color': 'gray'
        }
    }
    
    return status_mapping.get(payment_transaction.status, {
        'step': 0,
        'total_steps': 4,
        'current_step': 'Unknown Status',
        'description': 'Payment status is unknown',
        'icon': 'question',
        'color': 'gray'
    })
