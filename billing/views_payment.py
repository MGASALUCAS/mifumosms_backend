"""
Payment views for ZenoPay integration with user-friendly progress tracking.
Enhanced with Flask-style payment management functionality.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging
import uuid

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    SMSPackage, SMSBalance, Purchase, PaymentTransaction,
    UsageRecord, BillingPlan, Subscription
)
from .serializers import (
    SMSPackageSerializer, PurchaseSerializer, PurchaseCreateSerializer,
    SMSBalanceSerializer, UsageRecordSerializer, BillingPlanSerializer,
    SubscriptionSerializer, PaymentTransactionSerializer, PaymentInitiateSerializer
)
from .zenopay_service import zenopay_service

logger = logging.getLogger(__name__)


# ==============================
# LIST / DETAIL VIEWS
# ==============================

class PaymentTransactionListView(generics.ListAPIView):
    """
    List payment transactions for tenant.
    GET /api/billing/payments/transactions/
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["status", "payment_method", "currency", "created_at"]
    ordering_fields = ["created_at", "amount", "status"]
    ordering = ["-created_at"]
    search_fields = ["order_id", "invoice_number", "zenopay_order_id", "zenopay_reference"]

    def get_queryset(self):
        # During schema generation, drf_yasg sets swagger_fake_view = True and user is Anonymous
        if getattr(self, "swagger_fake_view", False):
            return PaymentTransaction.objects.none()

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            return PaymentTransaction.objects.none()

        return PaymentTransaction.objects.filter(tenant=tenant).order_by("-created_at")


class PaymentTransactionDetailView(generics.RetrieveAPIView):
    """
    Get payment transaction details.
    GET /api/billing/payments/transactions/{id}/
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PaymentTransaction.objects.none()

        tenant = getattr(self.request.user, "tenant", None)
        if not tenant:
            return PaymentTransaction.objects.none()

        return PaymentTransaction.objects.filter(tenant=tenant)


# ==============================
# ACTION ENDPOINTS
# ==============================

@swagger_auto_schema(
    method="post",
    operation_description="Initiate payment with ZenoPay for an SMS package with mobile money provider selection.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["package_id", "buyer_email", "buyer_name", "buyer_phone"],
        properties={
            "package_id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="SMS Package ID"),
            "buyer_email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description="Customer email address"),
            "buyer_name": openapi.Schema(type=openapi.TYPE_STRING, description="Customer full name"),
            "buyer_phone": openapi.Schema(type=openapi.TYPE_STRING, description="Customer phone number (07XXXXXXXX or 06XXXXXXXX)"),
            "mobile_money_provider": openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=["vodacom", "tigo", "airtel", "halotel"],
                description="Mobile money provider code (default: vodacom)"
            )
        },
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
                        "amount": 150000.00,
                        "currency": "TZS",
                        "mobile_money_provider": "vodacom",
                        "provider_name": "Vodacom",
                        "credits": 5000,
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
def initiate_payment(request):
    """
    Initiate payment with ZenoPay for SMS package purchase.
    POST /api/billing/payments/initiate/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        package_id = request.data.get('package_id')
        buyer_email = request.data.get('buyer_email')
        buyer_name = request.data.get('buyer_name')
        buyer_phone = request.data.get('buyer_phone')
        mobile_money_provider = request.data.get('mobile_money_provider', 'vodacom')

        if not all([package_id, buyer_email, buyer_name, buyer_phone]):
            return Response({
                'success': False,
                'message': 'Missing required fields: package_id, buyer_email, buyer_name, buyer_phone'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate mobile money provider
        valid_providers = ['vodacom', 'halotel', 'tigo', 'airtel']
        if mobile_money_provider not in valid_providers:
            return Response({
                'success': False,
                'message': f'Invalid mobile money provider. Choose from: {", ".join(valid_providers)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate phone number format (07 or 06)
        if not buyer_phone.startswith(('07', '06')):
            return Response({
                'success': False,
                'message': 'Invalid phone number. Must be a Tanzanian mobile number starting with 07 or 06 (e.g., 0744963858)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate package_id format
        try:
            # Try to convert to UUID to validate format
            uuid.UUID(package_id)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'message': f'Invalid package ID format: {package_id}. Please select a valid package.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            package = SMSPackage.objects.get(id=package_id, is_active=True)
        except SMSPackage.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Package not found or inactive. Please select a valid package.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            internal_order_id = f"MIFUMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            zenopay_order_id = zenopay_service.generate_order_id()
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            base_url = getattr(settings, "BASE_URL", "").rstrip("/")
            if not base_url:
                logger.warning("BASE_URL is not set; webhook URL will be relative.")
            webhook_url = f"{base_url}/api/billing/payments/webhook/".replace("//api", "/api") if base_url else "/api/billing/payments/webhook/"

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
                invoice_number=invoice_number,
                amount=package.price,
                credits=package.credits,
                unit_price=package.unit_price,
                payment_method='zenopay_mobile_money',
                status='pending'
            )

            # Initiate payment with ZenoPay
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
                # Store raw response for audit
                payment_transaction.webhook_data = payment_response.get('data', {})
                payment_transaction.status = 'pending'
                payment_transaction.save()

                return Response({
                    'success': True,
                    'message': 'Payment initiated successfully. Please complete payment on your mobile device.',
                    'data': {
                        'transaction_id': str(payment_transaction.id),
                        'order_id': internal_order_id,
                        'zenopay_order_id': zenopay_order_id,
                        'invoice_number': invoice_number,
                        'amount': float(package.price),
                        'currency': 'TZS',
                        'credits': package.credits,
                        'status': 'pending',
                        'mobile_money_provider': mobile_money_provider,
                        'provider_name': mobile_money_provider.title(),
                        'payment_instructions': (payment_response.get('data') or {}).get('message', ''),
                        'reference': payment_response.get('reference', ''),
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
                        },
                        'progress': {
                            'step': 1,
                            'total_steps': 4,
                            'current_step': 'Payment Initiated',
                            'next_step': 'Complete Payment on Mobile',
                            'completed_steps': ['Payment Initiated'],
                            'remaining_steps': ['Complete Payment on Mobile', 'Payment Verification', 'Credits Added'],
                            'percentage': 25,
                            'status_color': 'blue',
                            'status_icon': 'clock'
                        }
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                err_msg = payment_response.get('error', 'Payment initiation failed')
                payment_transaction.mark_as_failed(err_msg)
                purchase.mark_as_failed()
                return Response({
                    'success': False,
                    'message': 'Failed to initiate payment',
                    'error': err_msg
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Payment initiation error")
        return Response({
            'success': False,
            'message': 'Failed to initiate payment',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('transaction_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="PaymentTransaction UUID", required=True)
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """
    Check payment status and update progress.
    GET /api/billing/payments/transactions/{transaction_id}/status/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_transaction = get_object_or_404(PaymentTransaction, id=transaction_id, tenant=tenant)

        status_response = zenopay_service.check_payment_status(payment_transaction.zenopay_order_id) or {}
        ok = status_response.get('success', False)

        if ok:
            # Defensive gets
            payment_transaction.zenopay_reference = status_response.get('reference') or payment_transaction.zenopay_reference
            payment_transaction.zenopay_transid = status_response.get('transid') or payment_transaction.zenopay_transid
            payment_transaction.zenopay_channel = status_response.get('channel') or payment_transaction.zenopay_channel
            payment_transaction.zenopay_msisdn = status_response.get('msisdn') or payment_transaction.zenopay_msisdn
            if 'data' in status_response:
                payment_transaction.webhook_data = status_response['data']
            payment_transaction.save()

            progress = _get_payment_progress(payment_transaction, status_response)

            payment_status = (status_response.get('payment_status') or '').upper()
            if payment_status == 'SUCCESS' and payment_transaction.status in ('pending', 'processing'):
                payment_transaction.mark_as_completed(status_response.get('data', {}))
                if getattr(payment_transaction, 'purchase', None):
                    payment_transaction.purchase.complete_purchase()

                # refresh progress after state change
                progress = _get_payment_progress(payment_transaction, {"success": True, "payment_status": "SUCCESS"})

            return Response({
                'success': True,
                'data': {
                    'transaction_id': str(payment_transaction.id),
                    'order_id': payment_transaction.order_id,
                    'status': payment_transaction.status,
                    'payment_status': payment_status or 'UNKNOWN',
                    'amount': float(payment_transaction.amount),
                    'reference': status_response.get('reference', '') or '',
                    'progress': progress,
                    'updated_at': payment_transaction.updated_at.isoformat()
                }
            })

        return Response({
            'success': False,
            'message': 'Failed to check payment status',
            'error': status_response.get('error', 'Unknown error occurred')
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Payment status check error")
        return Response({
            'success': False,
            'message': 'Failed to check payment status',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Internal order ID", required=True)
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_payment(request, order_id):
    """
    Verify payment status by order_id (similar to Flask verify_payment).
    GET /api/billing/payments/verify/{order_id}/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_transaction = PaymentTransaction.objects.filter(
            order_id=order_id, tenant=tenant, user=request.user
        ).first()

        if not payment_transaction:
            logger.warning(f"Payment verification failed: No payment found for order_id {order_id} and user {request.user.id}")
            return Response({
                'success': False,
                'message': 'Payment not found.',
                'error_code': 'PAYMENT_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)

        # Already resolved?
        if payment_transaction.status not in ['pending', 'processing']:
            return Response({
                'success': payment_transaction.status == 'completed',
                'status': payment_transaction.status,
                'amount': float(payment_transaction.amount),
                'transaction_reference': payment_transaction.zenopay_reference or 'N/A',
                'message': 'Payment status already resolved.',
                'last_checked': payment_transaction.updated_at.isoformat()
            })

        status_response = zenopay_service.check_payment_status(payment_transaction.zenopay_order_id) or {}
        if status_response.get('success'):
            payment_status = (status_response.get('payment_status') or 'UNKNOWN').lower()
            payment_transaction.zenopay_reference = status_response.get('reference') or payment_transaction.zenopay_reference
            payment_transaction.zenopay_transid = status_response.get('transid') or payment_transaction.zenopay_transid
            payment_transaction.zenopay_channel = status_response.get('channel') or payment_transaction.zenopay_channel
            payment_transaction.zenopay_msisdn = status_response.get('msisdn') or payment_transaction.zenopay_msisdn
            if 'data' in status_response:
                payment_transaction.webhook_data = status_response['data']

            if payment_status in ('success', 'completed'):
                payment_transaction.mark_as_completed(status_response.get('data', {}))
                if getattr(payment_transaction, 'purchase', None):
                    payment_transaction.purchase.complete_purchase()
                status_message = 'Payment verified and completed successfully! Credits have been added to your account.'
            elif payment_status == 'failed':
                payment_transaction.mark_as_failed('Payment failed via verification')
                if getattr(payment_transaction, 'purchase', None):
                    payment_transaction.purchase.mark_as_failed()
                status_message = 'Payment verification failed. Please try again or contact support.'
            else:
                status_message = f'Payment status: {payment_status}. Please try again or contact support.'

            payment_transaction.save()

            return Response({
                'success': payment_transaction.status == 'completed',
                'status': payment_transaction.status,
                'amount': float(payment_transaction.amount),
                'transaction_reference': payment_transaction.zenopay_reference or 'N/A',
                'message': status_message,
                'last_checked': payment_transaction.updated_at.isoformat()
            })

        # ZenoPay says not found / error
        err = (status_response.get('error') or '').lower()
        if 'not found' in err:
            logger.warning(f"Payment {order_id} not found in ZenoPay (may have expired)")
            payment_transaction.status = 'expired'
            payment_transaction.error_message = 'Payment session expired or not found'
            payment_transaction.save()
            return Response({
                'success': False,
                'message': 'Payment session expired. Please initiate a new payment.',
                'error_code': 'PAYMENT_EXPIRED',
                'status': 'expired'
            }, status=status.HTTP_404_NOT_FOUND)

        logger.error(f"Payment verification failed for order {order_id}: {status_response.get('error')}")
        return Response({
            'success': False,
            'message': 'Failed to verify payment status. Please try again or contact support.',
            'error_code': 'PAYMENT_VERIFICATION_FAILED',
            'detail': status_response.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.exception("Payment verification error")
        return Response({
            'success': False,
            'message': 'Failed to verify payment status. Please try again or contact support.',
            'error_code': 'PAYMENT_VERIFICATION_FAILED',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_description="Webhook endpoint for ZenoPay notifications.",
    responses={200: openapi.Response(description="Processed")}
)
@api_view(['POST'])
@permission_classes([])  # Webhooks are external, no user authentication required
def payment_webhook(request):
    """
    Handle ZenoPay webhook notifications.
    POST /api/billing/payments/webhook/
    """
    try:
        # Optional: simple shared-secret header check
        expected_key = getattr(settings, "ZENOPAY_WEBHOOK_KEY", None)
        provided_key = request.headers.get("X-Zenopay-Key")
        if expected_key and provided_key != expected_key:
            logger.warning("Webhook auth failed")
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        webhook_data = request.data
        logger.info(f"Received ZenoPay webhook: {webhook_data}")

        webhook_response = zenopay_service.process_webhook(webhook_data) or {}

        if webhook_response.get('success'):
            order_id = webhook_response.get('order_id')
            payment_status = webhook_response.get('payment_status')

            try:
                payment_transaction = PaymentTransaction.objects.get(zenopay_order_id=order_id)
                if payment_status == 'COMPLETED':
                    payment_transaction.mark_as_completed(webhook_data)
                    if getattr(payment_transaction, 'purchase', None):
                        payment_transaction.purchase.complete_purchase()
                elif payment_status == 'FAILED':
                    payment_transaction.mark_as_failed('Payment failed via webhook')
                    if getattr(payment_transaction, 'purchase', None):
                        payment_transaction.purchase.mark_as_failed()
                else:
                    # Keep data but do not flip state
                    payment_transaction.webhook_data = webhook_data
                    payment_transaction.save()

                logger.info(f"Updated payment transaction {payment_transaction.id} to {payment_status}")
                return Response({'success': True, 'message': 'Webhook processed successfully'})
            except PaymentTransaction.DoesNotExist:
                logger.error(f"Payment transaction not found for zenopay_order_id: {order_id}")
                return Response({'success': False, 'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'message': 'Webhook processing failed', 'error': webhook_response.get('error')},
                            status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Webhook processing error")
        return Response({'success': False, 'message': 'Webhook processing failed', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('transaction_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="PaymentTransaction UUID", required=True)
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_progress(request, transaction_id):
    """
    Get detailed payment progress for user-friendly display.
    GET /api/billing/payments/transactions/{transaction_id}/progress/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_transaction = get_object_or_404(PaymentTransaction, id=transaction_id, tenant=tenant)

        status_response = zenopay_service.check_payment_status(payment_transaction.zenopay_order_id) or {}
        progress = _get_payment_progress(payment_transaction, status_response)

        purchase_data = None
        if getattr(payment_transaction, 'purchase', None):
            purchase_data = {
                'package_name': payment_transaction.purchase.package.name,
                'credits': payment_transaction.purchase.credits,
                'unit_price': float(payment_transaction.purchase.unit_price)
            }

        return Response({
            'success': True,
            'data': {
                'transaction_id': str(payment_transaction.id),
                'order_id': payment_transaction.order_id,
                'invoice_number': payment_transaction.invoice_number,
                'amount': float(payment_transaction.amount),
                'currency': payment_transaction.currency,
                'status': payment_transaction.status,
                'payment_status': (status_response.get('payment_status') or 'UNKNOWN') if status_response.get('success') else 'UNKNOWN',
                'progress': progress,
                'purchase': purchase_data,
                'created_at': payment_transaction.created_at.isoformat(),
                'updated_at': payment_transaction.updated_at.isoformat(),
                'completed_at': payment_transaction.completed_at.isoformat() if payment_transaction.completed_at else None
            }
        })

    except Exception as e:
        logger.exception("Payment progress error")
        return Response({'success': False, 'message': 'Failed to get payment progress', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_payment_progress(payment_transaction, status_response):
    """
    Calculate payment progress for user-friendly display.
    """
    progress = {
        'step': 1,
        'total_steps': 4,
        'current_step': 'Payment Initiated',
        'next_step': 'Complete Payment on Mobile',
        'completed_steps': ['Payment Initiated'],
        'remaining_steps': ['Complete Payment on Mobile', 'Payment Verification', 'Credits Added'],
        'percentage': 25,
        'status_color': 'blue',
        'status_icon': 'clock'
    }

    if payment_transaction.status == 'processing':
        progress.update({
            'step': 2,
            'current_step': 'Payment Processing',
            'next_step': 'Payment Verification',
            'completed_steps': ['Payment Initiated', 'Payment Processing'],
            'remaining_steps': ['Payment Verification', 'Credits Added'],
            'percentage': 50,
            'status_color': 'yellow',
            'status_icon': 'sync'
        })
    elif payment_transaction.status == 'completed':
        progress.update({
            'step': 4,
            'current_step': 'Payment Completed',
            'next_step': None,
            'completed_steps': ['Payment Initiated', 'Complete Payment on Mobile', 'Payment Verification', 'Credits Added'],
            'remaining_steps': [],
            'percentage': 100,
            'status_color': 'green',
            'status_icon': 'check'
        })
    elif payment_transaction.status == 'failed':
        progress.update({
            'current_step': 'Payment Failed',
            'next_step': 'Retry Payment',
            'status_color': 'red',
            'status_icon': 'x',
            'error_message': payment_transaction.error_message
        })
    elif status_response.get('success') and (status_response.get('payment_status') or '').upper() == 'SUCCESS':
        progress.update({
            'step': 3,
            'current_step': 'Payment Verified',
            'next_step': 'Credits Added',
            'completed_steps': ['Payment Initiated', 'Complete Payment on Mobile', 'Payment Verification'],
            'remaining_steps': ['Credits Added'],
            'percentage': 75,
            'status_color': 'blue',
            'status_icon': 'check-circle'
        })

    return progress


@swagger_auto_schema(method="get", responses={200: openapi.Response(description="Active payments list")})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_payments(request):
    """
    Get active payment processes for the current user.
    GET /api/billing/payments/active/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_active_payments = {}
        expired_payments = []
        now = timezone.now()

        pending = PaymentTransaction.objects.filter(
            tenant=tenant, user=request.user, status__in=['pending', 'processing']
        ).order_by('-created_at')

        for payment in pending:
            elapsed = (now - payment.created_at).total_seconds()
            if elapsed > 1800:
                payment.status = 'expired'
                payment.error_message = 'Payment session expired'
                payment.save()
                expired_payments.append({
                    'transaction_id': str(payment.id),
                    'order_id': payment.order_id,
                    'amount': float(payment.amount),
                    'reason': 'timeout'
                })
            else:
                user_active_payments[str(payment.id)] = {
                    'transaction_id': str(payment.id),
                    'order_id': payment.order_id,
                    'invoice_number': payment.invoice_number,
                    'amount': float(payment.amount),
                    'status': payment.status,
                    'created_at': payment.created_at.isoformat(),
                    'updated_at': payment.updated_at.isoformat(),
                    'timeout_in': max(0, 1800 - elapsed)
                }

        return Response({
            'success': True,
            'active_payments': user_active_payments,
            'expired_payments': expired_payments,
            'count': len(user_active_payments)
        })

    except Exception as e:
        logger.exception("Get active payments error")
        return Response({'success': False, 'message': 'Failed to get active payments', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    manual_parameters=[
        openapi.Parameter('transaction_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="PaymentTransaction UUID", required=True)
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_payment(request, transaction_id):
    """
    Cancel an active payment.
    POST /api/billing/payments/transactions/{transaction_id}/cancel/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_transaction = get_object_or_404(PaymentTransaction, id=transaction_id, tenant=tenant, user=request.user)

        if payment_transaction.status not in ['pending', 'processing']:
            return Response({'success': False, 'message': 'Payment cannot be cancelled. It is already completed or failed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_transaction.mark_as_cancelled()
        if getattr(payment_transaction, 'purchase', None):
            payment_transaction.purchase.status = 'cancelled'
            payment_transaction.purchase.save()

        logger.info(f"Payment {payment_transaction.order_id} cancelled by user {request.user.id}")

        return Response({'success': True, 'message': 'Payment cancelled successfully.', 'cancelled_order': payment_transaction.order_id})

    except Exception as e:
        logger.exception("Cancel payment error")
        return Response({'success': False, 'message': 'Failed to cancel payment', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method="post", responses={200: openapi.Response(description="Cleanup complete")})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_payments(request):
    """
    Clean up expired payment processes.
    POST /api/billing/payments/cleanup/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        stale_threshold = timezone.now() - timedelta(hours=1)
        cleaned_count = 0

        stale_payments = PaymentTransaction.objects.filter(
            tenant=tenant, user=request.user, status='pending', created_at__lt=stale_threshold
        )

        for payment in stale_payments:
            status_response = zenopay_service.check_payment_status(payment.zenopay_order_id) or {}
            if status_response.get('success'):
                st = (status_response.get('payment_status') or 'UNKNOWN').lower()
                if st in ('success', 'completed'):
                    payment.mark_as_completed(status_response.get('data', {}))
                    if getattr(payment, 'purchase', None):
                        payment.purchase.complete_purchase()
                else:
                    payment.status = 'expired'
                    payment.error_message = 'Payment expired (system cleanup)'
                    payment.save()
            else:
                payment.status = 'expired'
                payment.error_message = 'Payment expired (verification failed)'
                payment.save()

            cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} expired payment processes for user {request.user.id}")

        return Response({'success': True, 'message': f'Cleaned up {cleaned_count} expired payment processes.', 'cleaned_count': cleaned_count})

    except Exception as e:
        logger.exception("Cleanup payments error")
        return Response({'success': False, 'message': 'Failed to cleanup payments', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================
# MOBILE MONEY PROVIDERS ENDPOINT
# ==============================

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
def get_mobile_money_providers(request):
    """
    Get available mobile money providers for payment.
    GET /api/billing/payments/providers/
    """
    try:
        providers = [
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

# ==============================
# ENHANCED PAYMENT ENDPOINTS
# ==============================

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
    POST /api/billing/payments/initiate-enhanced/
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
                unit_price=package.unit_price,
                invoice_number=invoice_number,
                payment_method='zenopay_mobile_money',
                status='pending'
            )

            # Initiate ZenoPay payment
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
