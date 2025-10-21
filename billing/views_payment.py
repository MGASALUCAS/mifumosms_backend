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
    UsageRecord, BillingPlan, Subscription, CustomSMSPurchase
)
from .serializers import (
    SMSPackageSerializer, PurchaseSerializer, PurchaseCreateSerializer,
    SMSBalanceSerializer, UsageRecordSerializer, BillingPlanSerializer,
    SubscriptionSerializer, PaymentTransactionSerializer, PaymentInitiateSerializer,
    CustomSMSPurchaseSerializer, CustomSMSPurchaseCreateSerializer
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
        valid_providers = [p['code'] for p in get_mobile_money_providers_data()]
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
                # Keep status as pending until ZenoPay confirms COMPLETED or FAILED
                if payment_transaction.status != 'pending':
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
                        'provider_name': get_provider_name(mobile_money_provider),
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
                            'step': 2,
                            'total_steps': 4,
                            'current_step': 'Complete Payment on Mobile',
                            'next_step': 'Payment Verification',
                            'completed_steps': ['Payment Initiated'],
                            'remaining_steps': ['Payment Verification', 'Credits Added'],
                            'percentage': 33,
                            'status_color': 'yellow',
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

        # Add delay to ensure push notification stays visible for at least 1 minute
        import time
        time.sleep(60)  # Wait 1 minute to ensure push notification is visible

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

            # Check if payment is actually completed according to ZenoPay API
            # According to ZenoPay docs: result should be "SUCCESS" and payment_status should be "COMPLETED"
            result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay (SUCCESS/FAIL)
            payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
            payment_status = payment_data.get('payment_status', '').upper()  # This is the actual payment status (COMPLETED/FAILED/CANCELLED)
            
            # Map ZenoPay status directly: SUCCESS = completed, FAILED = failed, anything else = pending
            require_webhook = getattr(settings, 'ZENOPAY_REQUIRE_WEBHOOK', False)
            if result == 'SUCCESS' and payment_status == 'COMPLETED':
                # Only mark completed if webhook received when strict mode is on
                if not require_webhook or getattr(payment_transaction, 'webhook_received', False):
                    payment_transaction.mark_as_completed(status_response.get('data', {}))
                    if getattr(payment_transaction, 'purchase', None):
                        payment_transaction.purchase.complete_purchase()
                else:
                    # Await webhook confirmation
                    if payment_transaction.status != 'pending':
                        payment_transaction.status = 'pending'
                        payment_transaction.save()

                # refresh progress after state change
                progress = _get_payment_progress(payment_transaction, {"success": True, "payment_status": "COMPLETED"})
            elif result == 'FAILED' or payment_status == 'FAILED' or payment_status == 'CANCELLED':
                # Handle payment failure or cancellation
                if payment_status == 'CANCELLED':
                    payment_transaction.mark_as_failed('Payment cancelled by user or expired')
                else:
                    payment_transaction.mark_as_failed('Payment failed - user did not complete payment or network issue')
            else:
                # Keep as pending if not explicitly SUCCESS/COMPLETED or FAILED
                if payment_transaction.status != 'pending':
                    payment_transaction.status = 'pending'
                    payment_transaction.save()
                progress = _get_payment_progress(payment_transaction, {"success": False, "payment_status": "PENDING"})
            
            if not status_response.get('success'):
                # Handle network issues or API errors
                payment_transaction.mark_as_failed('Payment verification failed - network issue or API error')
                if getattr(payment_transaction, 'purchase', None):
                    payment_transaction.purchase.mark_as_failed()
                progress = _get_payment_progress(payment_transaction, {"success": False, "payment_status": "ERROR"})

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

        # Add delay to ensure push notification stays visible for at least 1 minute
        import time
        time.sleep(60)  # Wait 1 minute to ensure push notification is visible

        status_response = zenopay_service.check_payment_status(payment_transaction.zenopay_order_id) or {}
        if status_response.get('success'):
            # Get the actual payment status from ZenoPay response
            result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay
            payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
            payment_status = payment_data.get('payment_status', '').upper()
            
            payment_transaction.zenopay_reference = status_response.get('reference') or payment_transaction.zenopay_reference
            payment_transaction.zenopay_transid = status_response.get('transid') or payment_transaction.zenopay_transid
            payment_transaction.zenopay_channel = status_response.get('channel') or payment_transaction.zenopay_channel
            payment_transaction.zenopay_msisdn = status_response.get('msisdn') or payment_transaction.zenopay_msisdn
            if 'data' in status_response:
                payment_transaction.webhook_data = status_response['data']

            # Map ZenoPay status directly: SUCCESS = completed, FAILED = failed, anything else = pending
            if result == 'SUCCESS' and payment_status == 'COMPLETED':
                require_webhook = getattr(settings, 'ZENOPAY_REQUIRE_WEBHOOK', False)
                if not require_webhook or getattr(payment_transaction, 'webhook_received', False):
                    payment_transaction.mark_as_completed(status_response.get('data', {}))
                    if getattr(payment_transaction, 'purchase', None):
                        payment_transaction.purchase.complete_purchase()
                else:
                    if payment_transaction.status != 'pending':
                        payment_transaction.status = 'pending'
                        payment_transaction.save()
                status_message = 'Payment verified and completed successfully! Credits have been added to your account.'
            elif payment_status == 'FAILED' or result == 'FAILED' or payment_status == 'CANCELLED':
                if payment_status == 'CANCELLED':
                    payment_transaction.mark_as_failed('Payment cancelled by user or expired')
                    status_message = 'Payment was cancelled. Please try again if you want to purchase credits.'
                else:
                    payment_transaction.mark_as_failed('Payment failed - user did not complete payment or network issue')
                    status_message = 'Payment failed. Please try again or contact support.'
                if getattr(payment_transaction, 'purchase', None):
                    payment_transaction.purchase.mark_as_failed()
            else:
                # Keep as pending if not explicitly SUCCESS/COMPLETED or FAILED
                if payment_transaction.status != 'pending':
                    payment_transaction.status = 'pending'
                    payment_transaction.save()
                # Payment is still processing or in unknown state
                status_message = f'Payment is being processed. Status: {payment_status or result}. Please wait a moment and try again.'

            payment_transaction.save()

            return Response({
                'success': payment_transaction.status == 'completed',
                'status': payment_transaction.status,
                'amount': float(payment_transaction.amount),
                'transaction_reference': payment_transaction.zenopay_reference or 'N/A',
                'message': status_message,
                'last_checked': payment_transaction.updated_at.isoformat()
            })

        # Handle ZenoPay API errors
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
        elif 'network' in err or 'timeout' in err or 'connection' in err:
            logger.error(f"Network error during payment verification for order {order_id}: {status_response.get('error')}")
            return Response({
                'success': False,
                'message': 'Network error occurred. Please check your connection and try again.',
                'error_code': 'NETWORK_ERROR',
                'detail': 'Unable to verify payment due to network issues'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_pending_payments(request):
    """
    Poll ZenoPay for all pending payments for the tenant and update their statuses.
    POST /api/billing/payments/sync/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant.'}, status=status.HTTP_400_BAD_REQUEST)

        updated = 0
        failed = 0
        checked = 0
        results = []

        pending_payments = PaymentTransaction.objects.filter(tenant=tenant, status='pending')

        for payment in pending_payments:
            checked += 1
            status_response = zenopay_service.check_payment_status(payment.zenopay_order_id) or {}
            if status_response.get('success'):
                result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay (SUCCESS/FAIL)
                payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
                payment_status = payment_data.get('payment_status', '').upper()  # This is the actual payment status (COMPLETED/FAILED/CANCELLED)

                if result == 'SUCCESS' and payment_status == 'COMPLETED':
                    payment.mark_as_completed(status_response.get('data', {}))
                    if getattr(payment, 'purchase', None):
                        payment.purchase.complete_purchase()
                    updated += 1
                    results.append({'id': str(payment.id), 'status': 'completed'})
                elif result == 'FAILED' or payment_status == 'FAILED' or payment_status == 'CANCELLED':
                    if payment_status == 'CANCELLED':
                        payment.mark_as_failed('Payment cancelled by user or expired via sync')
                    else:
                        payment.mark_as_failed('Payment failed via sync')
                    if getattr(payment, 'purchase', None):
                        payment.purchase.mark_as_failed()
                    updated += 1
                    results.append({'id': str(payment.id), 'status': 'failed'})
                else:
                    results.append({'id': str(payment.id), 'status': 'pending'})
            else:
                failed += 1
                results.append({'id': str(payment.id), 'status': 'error', 'error': status_response.get('error', 'Unknown error')})

        return Response({
            'success': True,
            'data': {
                'checked': checked,
                'updated': updated,
                'failed_checks': failed,
                'results': results
            }
        })
    except Exception as e:
        logger.exception('Sync pending payments error')
        return Response({'success': False, 'message': 'Failed to sync payments', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        # Validate webhook authentication using ZenoPay API key
        # According to ZenoPay docs, they send x-api-key in the header
        expected_key = getattr(settings, "ZENOPAY_API_KEY", None)
        provided_key = request.headers.get("x-api-key")
        
        if not expected_key:
            logger.error("ZENOPAY_API_KEY not configured for webhook validation")
            return Response({'success': False, 'message': 'Webhook authentication not configured'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if provided_key != expected_key:
            logger.warning(f"Webhook authentication failed. Expected: {expected_key[:8]}..., Got: {provided_key[:8] if provided_key else 'None'}...")
            return Response({'success': False, 'message': 'Unauthorized webhook request'}, 
                          status=status.HTTP_401_UNAUTHORIZED)

        webhook_data = request.data
        logger.info(f"Received ZenoPay webhook: {webhook_data}")

        webhook_response = zenopay_service.process_webhook(webhook_data) or {}

        if webhook_response.get('success'):
            order_id = webhook_response.get('order_id')
            payment_status = webhook_response.get('payment_status')

            try:
                payment_transaction = PaymentTransaction.objects.get(zenopay_order_id=order_id)
                
                # Additional verification: Check with ZenoPay API to confirm the payment status
                # This prevents webhook spoofing and ensures the payment is actually completed
                if payment_status == 'COMPLETED':
                    # Verify with ZenoPay API before marking as completed
                    verification_response = zenopay_service.check_payment_status(order_id)
                    if verification_response.get('success'):
                        result = (verification_response.get('payment_status') or '').upper()
                        payment_data = verification_response.get('data', {}).get('data', [{}])[0] if verification_response.get('data', {}).get('data') else {}
                        verified_payment_status = payment_data.get('payment_status', '').upper()
                        
                        # Map ZenoPay status directly: SUCCESS = completed, FAILED = failed, anything else = pending
                        if result == 'SUCCESS' and verified_payment_status == 'COMPLETED':
                            payment_transaction.webhook_received = True
                            payment_transaction.mark_as_completed(webhook_data)
                            if getattr(payment_transaction, 'purchase', None):
                                payment_transaction.purchase.complete_purchase()
                            logger.info(f"Payment transaction {payment_transaction.id} verified and completed via webhook")
                        elif result == 'FAILED' or verified_payment_status == 'FAILED' or verified_payment_status == 'CANCELLED':
                            if verified_payment_status == 'CANCELLED':
                                payment_transaction.mark_as_failed('Payment cancelled by user or expired via webhook')
                            else:
                                payment_transaction.mark_as_failed('Payment failed via webhook verification')
                            if getattr(payment_transaction, 'purchase', None):
                                payment_transaction.purchase.mark_as_failed()
                            logger.info(f"Payment transaction {payment_transaction.id} marked as failed via webhook")
                        else:
                            # Keep as pending if not explicitly SUCCESS/COMPLETED or FAILED
                            if payment_transaction.status != 'pending':
                                payment_transaction.status = 'pending'
                            payment_transaction.save()
                            logger.warning(f"Webhook status unclear for order {order_id}, keeping as pending")
                    else:
                        logger.warning(f"Failed to verify webhook with ZenoPay API for order {order_id}")
                        payment_transaction.webhook_data = webhook_data
                        payment_transaction.save()
                        
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
                'progress_percentage': progress.get('percentage', 0),
                'current_step': progress.get('current_step', ''),
                'next_step': progress.get('next_step', ''),
                'steps': progress.get('completed_steps', []) + progress.get('remaining_steps', []),
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
            'total_steps': 4,
            'current_step': 'Payment Processing',
            'next_step': 'Complete Payment on Mobile',
            'completed_steps': ['Payment Initiated', 'Payment Processing'],
            'remaining_steps': ['Complete Payment on Mobile', 'Payment Verification', 'Credits Added'],
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
    elif status_response.get('success'):
        # Check if payment is verified but not yet completed
        result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay (SUCCESS/FAIL)
        payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
        payment_status = payment_data.get('payment_status', '').upper()  # This is the actual payment status (COMPLETED/FAILED/CANCELLED)
        
        if result == 'SUCCESS' and payment_status == 'COMPLETED':
            # Payment is completed
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
        elif result == 'SUCCESS' and payment_status != 'COMPLETED':
            # Payment is verified but not completed - keep as pending
            progress.update({
                'step': 3,
                'current_step': 'Payment Verified',
                'next_step': 'Credits Added',
                'completed_steps': ['Payment Initiated', 'Complete Payment on Mobile', 'Payment Verification'],
                'remaining_steps': ['Credits Added'],
                'percentage': 75,
                'status_color': 'yellow',
                'status_icon': 'clock'
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

        # Check for expired payments (1 hour) and stuck processing payments (30 minutes)
        stale_threshold = timezone.now() - timedelta(hours=1)
        processing_threshold = timezone.now() - timedelta(minutes=30)
        cleaned_count = 0

        # Get both stale pending payments and stuck processing payments
        stale_payments = PaymentTransaction.objects.filter(
            tenant=tenant, user=request.user, 
            status__in=['pending', 'processing'], 
            created_at__lt=stale_threshold
        )
        
        # Also get processing payments that are stuck (older than 30 minutes)
        stuck_processing = PaymentTransaction.objects.filter(
            tenant=tenant, user=request.user,
            status='processing',
            created_at__lt=processing_threshold
        )
        
        # Combine both querysets
        all_stale_payments = stale_payments.union(stuck_processing)

        for payment in all_stale_payments:
            status_response = zenopay_service.check_payment_status(payment.zenopay_order_id) or {}
            if status_response.get('success'):
                # Check if payment is actually completed according to ZenoPay API
                result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay
                payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
                payment_status = payment_data.get('payment_status', '').upper()
                
                # Map ZenoPay status directly: SUCCESS = completed, FAILED = failed, anything else = pending
                if result == 'SUCCESS' and payment_status == 'COMPLETED':
                    payment.mark_as_completed(status_response.get('data', {}))
                    if getattr(payment, 'purchase', None):
                        payment.purchase.complete_purchase()
                elif result == 'FAILED' or payment_status == 'FAILED':
                    payment.mark_as_failed('Payment failed via cleanup verification')
                    if getattr(payment, 'purchase', None):
                        payment.purchase.mark_as_failed()
                else:
                    # Keep as pending if not explicitly SUCCESS/COMPLETED or FAILED
                    if payment.status != 'pending':
                        payment.status = 'pending'
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
        providers = get_mobile_money_providers_data()
        
        return Response({
            'success': True,
            'providers': providers,
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
# HELPER FUNCTIONS
# ==============================

def get_mobile_money_providers_data():
    """Get available mobile money providers with their details."""
    return [
        {
            'code': 'vodacom',
            'name': 'Vodacom M-Pesa',
            'description': 'Pay with M-Pesa via Vodacom',
            'icon': 'vodacom-icon',
            'popular': True,
            'is_active': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'tigo',
            'name': 'Tigo Pesa',
            'description': 'Pay with Tigo Pesa',
            'icon': 'tigo-icon',
            'popular': True,
            'is_active': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'airtel',
            'name': 'Airtel Money',
            'description': 'Pay with Airtel Money',
            'icon': 'airtel-icon',
            'popular': True,
            'is_active': True,
            'min_amount': 1000,
            'max_amount': 1000000
        },
        {
            'code': 'halotel',
            'name': 'Halotel',
            'description': 'Pay with Halotel',
            'icon': 'halotel-icon',
            'popular': False,
            'is_active': True,
            'min_amount': 1000,
            'max_amount': 500000
        }
    ]


def get_provider_name(code):
    """Get provider name by code."""
    providers = get_mobile_money_providers_data()
    for provider in providers:
        if provider['code'] == code:
            return provider['name']
    return code.title()


# ==============================
# CUSTOM SMS PURCHASE ENDPOINTS
# ==============================

@swagger_auto_schema(
    method="post",
    operation_description="Calculate pricing for custom SMS purchase.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["credits"],
        properties={
            "credits": openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of SMS credits (minimum 100)")
        },
    ),
    responses={
        200: openapi.Response(
            description="Pricing calculated successfully",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "credits": 5000,
                        "unit_price": 30.00,
                        "total_price": 150000.00,
                        "active_tier": "Lite",
                        "tier_min_credits": 1,
                        "tier_max_credits": 5000,
                        "savings_percentage": 0.0
                    }
                }
            }
        ),
        400: openapi.Response(description="Bad request - validation errors")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_custom_sms_pricing(request):
    """
    Calculate pricing for custom SMS purchase.
    POST /api/billing/payments/custom-sms/calculate/
    """
    try:
        credits = request.data.get('credits')
        
        if not credits:
            return Response({
                'success': False,
                'message': 'Credits amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if credits < 100:
            return Response({
                'success': False,
                'message': 'Minimum 100 SMS credits required for custom purchase'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a temporary CustomSMSPurchase to calculate pricing
        temp_purchase = CustomSMSPurchase(credits=credits)
        unit_price, total_price, active_tier, tier_min, tier_max = temp_purchase.calculate_pricing(credits)
        
        # Calculate savings percentage
        standard_rate = 30  # TZS per SMS
        savings_percentage = round(((standard_rate - unit_price) / standard_rate) * 100, 1) if unit_price < standard_rate else 0
        
        # Define pricing tiers for response
        pricing_tiers = [
            {'name': 'Lite', 'min_credits': 1, 'max_credits': 4999, 'unit_price': 30.00},
            {'name': 'Standard', 'min_credits': 5000, 'max_credits': 50000, 'unit_price': 25.00},
            {'name': 'Pro', 'min_credits': 50001, 'max_credits': 250000, 'unit_price': 18.00},
            {'name': 'Enterprise', 'min_credits': 250001, 'max_credits': 1000000, 'unit_price': 12.00},
        ]
        
        return Response({
            'success': True,
            'data': {
                'credits': credits,
                'unit_price': float(unit_price),
                'total_price': float(total_price),
                'active_tier': active_tier,
                'tier_min_credits': tier_min,
                'tier_max_credits': tier_max,
                'savings_percentage': savings_percentage,
                'pricing_tiers': pricing_tiers
            }
        })
        
    except Exception as e:
        logger.exception("Custom SMS pricing calculation error")
        return Response({
            'success': False,
            'message': 'Failed to calculate pricing',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_description="Initiate custom SMS purchase with ZenoPay.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["credits", "buyer_email", "buyer_name", "buyer_phone"],
        properties={
            "credits": openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of SMS credits (minimum 100)"),
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
            description="Custom SMS purchase initiated successfully",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Custom SMS purchase initiated successfully. Please complete payment on your mobile device.",
                    "data": {
                        "purchase_id": "uuid",
                        "credits": 5000,
                        "unit_price": 30.00,
                        "total_price": 150000.00,
                        "active_tier": "Lite",
                        "status": "processing",
                        "payment_instructions": "Request in progress. You will receive a callback shortly"
                    }
                }
            }
        ),
        400: openapi.Response(description="Bad request - validation errors")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_custom_sms_purchase(request):
    """
    Initiate custom SMS purchase with ZenoPay.
    POST /api/billing/payments/custom-sms/initiate/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomSMSPurchaseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        credits = validated_data['credits']
        buyer_email = validated_data['buyer_email']
        buyer_name = validated_data['buyer_name']
        buyer_phone = validated_data['buyer_phone']
        mobile_money_provider = validated_data.get('mobile_money_provider', 'vodacom')

        with transaction.atomic():
            # Create custom SMS purchase
            custom_purchase = CustomSMSPurchase.objects.create(
                tenant=tenant,
                credits=credits
            )
            
            # Calculate pricing
            unit_price, total_price, active_tier, tier_min, tier_max = custom_purchase.calculate_pricing(credits)
            custom_purchase.unit_price = unit_price
            custom_purchase.total_price = total_price
            custom_purchase.active_tier = active_tier
            custom_purchase.tier_min_credits = tier_min
            custom_purchase.tier_max_credits = tier_max
            custom_purchase.status = 'processing'
            custom_purchase.save()

            # Create payment transaction
            internal_order_id = f"CUSTOM-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            zenopay_order_id = zenopay_service.generate_order_id()
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            base_url = getattr(settings, "BASE_URL", "").rstrip("/")
            webhook_url = f"{base_url}/api/billing/payments/webhook/".replace("//api", "/api") if base_url else "/api/billing/payments/webhook/"

            payment_transaction = PaymentTransaction.objects.create(
                tenant=tenant,
                user=request.user,
                zenopay_order_id=zenopay_order_id,
                order_id=internal_order_id,
                invoice_number=invoice_number,
                amount=total_price,
                currency='TZS',
                buyer_email=buyer_email,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                payment_method='zenopay_mobile_money',
                mobile_money_provider=mobile_money_provider,
                webhook_url=webhook_url
            )

            # Link payment transaction to custom purchase
            custom_purchase.payment_transaction = payment_transaction
            custom_purchase.save()

            # Initiate payment with ZenoPay
            payment_response = zenopay_service.create_payment(
                order_id=zenopay_order_id,
                buyer_email=buyer_email,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                amount=total_price,
                webhook_url=webhook_url,
                mobile_money_provider=mobile_money_provider
            )

            if payment_response.get('success'):
                # Store raw response for audit
                payment_transaction.webhook_data = payment_response.get('data', {})
                # Keep status as pending until ZenoPay confirms COMPLETED or FAILED
                if payment_transaction.status != 'pending':
                    payment_transaction.status = 'pending'
                payment_transaction.save()

                return Response({
                    'success': True,
                    'message': 'Custom SMS purchase initiated successfully. Please complete payment on your mobile device.',
                    'data': {
                        'purchase_id': str(custom_purchase.id),
                        'transaction_id': str(payment_transaction.id),
                        'order_id': internal_order_id,
                        'zenopay_order_id': zenopay_order_id,
                        'invoice_number': invoice_number,
                        'credits': credits,
                        'unit_price': float(unit_price),
                        'total_price': float(total_price),
                        'active_tier': active_tier,
                        'tier_min_credits': tier_min,
                        'tier_max_credits': tier_max,
                        'status': 'pending',
                        'mobile_money_provider': mobile_money_provider,
                        'provider_name': get_provider_name(mobile_money_provider),
                        'payment_instructions': (payment_response.get('data') or {}).get('message', ''),
                        'reference': payment_response.get('reference', ''),
                        'buyer': {
                            'name': buyer_name,
                            'email': buyer_email,
                            'phone': buyer_phone
                        }
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                err_msg = payment_response.get('error', 'Payment initiation failed')
                custom_purchase.mark_as_failed(err_msg)
                payment_transaction.mark_as_failed(err_msg)
                return Response({
                    'success': False,
                    'message': 'Failed to initiate custom SMS purchase',
                    'error': err_msg
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Custom SMS purchase initiation error")
        return Response({
            'success': False,
            'message': 'Failed to initiate custom SMS purchase',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('purchase_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Custom SMS Purchase UUID", required=True)
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_custom_sms_purchase_status(request, purchase_id):
    """
    Check custom SMS purchase status.
    GET /api/billing/payments/custom-sms/{purchase_id}/status/
    """
    try:
        tenant = getattr(request.user, "tenant", None)
        if not tenant:
            return Response({'success': False, 'message': 'User is not associated with any tenant. Please contact support.'},
                            status=status.HTTP_400_BAD_REQUEST)

        custom_purchase = get_object_or_404(CustomSMSPurchase, id=purchase_id, tenant=tenant)

        if custom_purchase.payment_transaction:
            # Check payment status
            status_response = zenopay_service.check_payment_status(custom_purchase.payment_transaction.zenopay_order_id) or {}
            
            if status_response.get('success'):
                result = (status_response.get('payment_status') or '').upper()  # This is the 'result' field from ZenoPay (SUCCESS/FAIL)
                payment_data = status_response.get('data', {}).get('data', [{}])[0] if status_response.get('data', {}).get('data') else {}
                payment_status = payment_data.get('payment_status', '').upper()  # This is the actual payment status (COMPLETED/FAILED/CANCELLED)
                
                # Update payment transaction
                custom_purchase.payment_transaction.zenopay_reference = status_response.get('reference') or custom_purchase.payment_transaction.zenopay_reference
                custom_purchase.payment_transaction.zenopay_transid = status_response.get('transid') or custom_purchase.payment_transaction.zenopay_transid
                custom_purchase.payment_transaction.zenopay_channel = status_response.get('channel') or custom_purchase.payment_transaction.zenopay_channel
                custom_purchase.payment_transaction.zenopay_msisdn = status_response.get('msisdn') or custom_purchase.payment_transaction.zenopay_msisdn
                custom_purchase.payment_transaction.save()

                # Map ZenoPay status directly: SUCCESS = completed, FAILED = failed, anything else = pending
                if result == 'SUCCESS' and payment_status == 'COMPLETED':
                    custom_purchase.complete_purchase()
                    custom_purchase.payment_transaction.mark_as_completed(status_response.get('data', {}))
                elif payment_status == 'FAILED' or result == 'FAILED':
                    custom_purchase.mark_as_failed('Payment failed via verification')
                    custom_purchase.payment_transaction.mark_as_failed('Payment failed via verification')
                else:
                    # Keep as pending if not explicitly SUCCESS/COMPLETED or FAILED
                    if custom_purchase.status != 'pending':
                        custom_purchase.status = 'pending'
                        custom_purchase.save()

        return Response({
            'success': True,
            'data': {
                'purchase_id': str(custom_purchase.id),
                'credits': custom_purchase.credits,
                'unit_price': float(custom_purchase.unit_price),
                'total_price': float(custom_purchase.total_price),
                'active_tier': custom_purchase.active_tier,
                'status': custom_purchase.status,
                'created_at': custom_purchase.created_at.isoformat(),
                'updated_at': custom_purchase.updated_at.isoformat(),
                'completed_at': custom_purchase.completed_at.isoformat() if custom_purchase.completed_at else None
            }
        })

    except Exception as e:
        logger.exception("Custom SMS purchase status check error")
        return Response({
            'success': False,
            'message': 'Failed to check custom SMS purchase status',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

