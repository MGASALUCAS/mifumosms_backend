"""
SMS API Views with Beem Integration

This module provides REST API endpoints for SMS functionality using Beem Africa
as the primary SMS provider. It includes comprehensive error handling, validation,
and integration with the existing messaging system.

Endpoints:
- Send single SMS
- Send bulk SMS
- Schedule SMS
- Get delivery status
- Test Beem connection
- Get account balance
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import logging

from .models import Message, Conversation, Contact
from .models_sms import SMSProvider, SMSSenderID, SMSTemplate, SMSMessage, SMSDeliveryReport
from billing.models import SMSBalance
from .services.beem_sms import BeemSMSService, BeemSMSError
from .serializers_sms_beem import (
    SMSSendSerializer,
    SMSBulkSendSerializer,
    SMSScheduleSerializer,
    SMSMessageSerializer,
    SMSDeliveryReportSerializer
)

logger = logging.getLogger(__name__)


def _error_response(message, status_code=status.HTTP_400_BAD_REQUEST, error_code=None, errors=None, detail=None, user_hint=None, actions=None):
    """Standard error payload for frontend-friendly display with guidance."""
    payload = {
        'success': False,
        'message': message,
    }
    if error_code:
        payload['error_code'] = error_code
    if errors:
        payload['errors'] = errors
    if detail:
        payload['detail'] = detail
    if user_hint:
        payload['user_hint'] = user_hint
    if actions:
        payload['actions'] = actions
    return Response(payload, status=status_code)


def _parse_provider_error(detail):
    """Extract provider error code and message from Beem error payloads."""
    try:
        import json
        # Detail may be a JSON string or a string like: "Beem API error: 400 - {json}"
        text = detail or ''
        json_part = None
        if isinstance(text, dict):
            json_part = text
        else:
            # Try direct JSON
            try:
                json_part = json.loads(text)
            except Exception:
                # Try to find JSON after a dash
                if ' - ' in text:
                    possible = text.split(' - ', 1)[1]
                    json_part = json.loads(possible)
        if isinstance(json_part, dict):
            data = json_part.get('data') or json_part
            code = data.get('code')
            message = data.get('message') or data.get('error')
            return code, message
    except Exception:
        pass
    return None, None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms(request):
    """
    Send SMS message via Beem Africa

    POST /api/messaging/sms/send/

    Request Body:
    {
        "message": "Hello from Mifumo WMS!",
        "recipients": ["255700000001", "255700000002"],
        "sender_id": "MIFUMO",
        "template_id": "uuid-optional",
        "schedule_time": "2024-01-01T10:00:00Z", // optional
        "encoding": 0 // optional, 0=GSM7, 1=UCS2
    }

    Response:
    {
        "success": true,
        "message": "SMS sent successfully",
        "data": {
            "message_id": "uuid",
            "provider": "beem",
            "recipient_count": 2,
            "cost_estimate": 0.10,
            "status": "queued"
        }
    }
    """
    try:
        serializer = SMSSendSerializer(data=request.data)
        if not serializer.is_valid():
            # Check if the error is related to special characters
            errors = serializer.errors
            has_special_chars = any('special characters' in str(error) for error in errors.get('message', []))
            
            if has_special_chars:
                return _error_response(
                    'Message contains special characters or emojis that are not allowed.',
                    status.HTTP_400_BAD_REQUEST,
                    error_code='INVALID_CHARACTERS',
                    errors=errors,
                    user_hint='Please use only plain text (letters, numbers, spaces, and basic punctuation). Remove emojis and special characters.',
                    actions={'allowed_chars': 'Letters, numbers, spaces, and basic punctuation only'}
                )
            else:
                return _error_response(
                    'Some information is missing or invalid.',
                    status.HTTP_400_BAD_REQUEST,
                    error_code='VALIDATION_ERROR',
                    errors=errors,
                    user_hint='Check the phone numbers and message, then try again.'
                )

        data = serializer.validated_data
        tenant = request.user.tenant

        # Check if user has a tenant
        if not tenant:
            return _error_response(
                'You are not linked to any organization.',
                status.HTTP_400_BAD_REQUEST,
                error_code='NO_TENANT',
                user_hint='Please contact support to link your account to an organization.'
            )

        # Get or create Beem provider
        beem_provider = get_or_create_beem_provider(tenant)

        # Get and validate sender ID (admin fallback to default)
        sender_id = data.get('sender_id')
        sender_id_obj = None
        if sender_id:
            sender_id_obj = get_sender_id(tenant, sender_id)
        
        if not sender_id_obj:
            # If admin, auto-use/create default sender ID
            if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
                sender_id_obj = get_or_create_default_sender(tenant, beem_provider)
            else:
                # Normal users: if requesting platform default, create it on-demand
                if (sender_id or '').strip().lower() == 'taarifa-sms':
                    sender_id_obj = get_or_create_default_sender(tenant, beem_provider)
                else:
                    return _error_response(
                        'Sender name is missing or not available.',
                        status.HTTP_400_BAD_REQUEST,
                        error_code='SENDER_ID_INVALID',
                        user_hint='Choose an approved sender name or request the default in Sender Names.',
                        actions={'request_default_url': '/api/messaging/sender-requests/request-default/', 'available_url': '/api/messaging/sender-requests/available/'}
                    )

        # Get template if provided
        template = None
        if data.get('template_id'):
            template = get_object_or_404(SMSTemplate, id=data['template_id'], tenant=tenant)
            message_content = template.message
        else:
            message_content = data['message']

        # Initialize Beem service
        beem_service = BeemSMSService()

        # Validate SMS sending capability before processing
        from .services.sms_validation import SMSValidationService, SMSValidationError
        
        validation_service = SMSValidationService(tenant)
        required_credits = len(data['recipients'])
        
        # Admin fallback: ensure sufficient credits
        if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
            balance, _ = SMSBalance.objects.get_or_create(tenant=tenant)
            if balance.credits < required_credits:
                top_up_amount = max(1000, required_credits - balance.credits)
                balance.add_credits(top_up_amount)
        
        validation_result = validation_service.validate_sms_sending(
            sender_id_obj.sender_id,
            required_credits=required_credits,
            message=message_content
        )
        
        if not validation_result['valid']:
            lack_credits = 'Insufficient SMS credits' in validation_result['error'] or validation_result.get('reason') == 'no_credits'
            message_too_long = validation_result.get('reason') == 'message_too_long'
            
            if message_too_long:
                return _error_response(
                    validation_result['error'],
                    status.HTTP_400_BAD_REQUEST,
                    error_code='MESSAGE_TOO_LONG',
                    detail=validation_result.get('error_type'),
                    user_hint='Please reduce your message length to 200 SMS segments or less.',
                    actions={'max_segments': 200, 'current_segments': validation_result.get('segments', 0)}
                )
            elif lack_credits:
                return _error_response(
                    validation_result['error'],
                    status.HTTP_400_BAD_REQUEST,
                    error_code='INSUFFICIENT_CREDITS',
                    detail=validation_result.get('error_type'),
                    user_hint='Buy SMS credits and try again.',
                    actions={'purchase_url': '/api/billing/sms/purchase/'}
                )
            else:
                return _error_response(
                    validation_result['error'],
                    status.HTTP_400_BAD_REQUEST,
                    error_code='VALIDATION_ERROR',
                    detail=validation_result.get('error_type'),
                    user_hint='Please review the details and try again.'
                )

        # Send SMS via Beem
        with transaction.atomic():
            # Create base message
            base_message = Message.objects.create(
                tenant=tenant,
                conversation=None,  # SMS doesn't use conversations
                direction='out',
                provider='sms',
                text=message_content,
                recipient_number=data['recipients'][0] if data['recipients'] else '',  # Store first recipient
                created_by=request.user
            )

            # Create SMS message record
            sms_message = SMSMessage.objects.create(
                tenant=tenant,
                base_message=base_message,
                provider=beem_provider,
                sender_id=sender_id_obj,
                template=template,
                status='queued'
            )

        # Send via Beem API (encoding will be auto-detected if not specified)
        try:
            beem_response = beem_service.send_sms(
                message=message_content,
                recipients=data['recipients'],
                source_addr=sender_id_obj.sender_id,
                schedule_time=data.get('schedule_time'),
                encoding=data.get('encoding')  # None will trigger auto-detection
            )
        except BeemSMSError as e:
            # Return Beem error payload to frontend with parsed provider reason
            beem_error = getattr(e, 'detail', None) or str(e)
            prov_code, prov_msg = _parse_provider_error(beem_error)
            user_msg = 'Your message could not be sent right now.'
            hint = 'Check the phone number format (+2557XXXXXXXX) and try again.'
            if prov_msg:
                user_msg = f"Provider error: {prov_msg}"
                # Specific hint for invalid sender id
                if (prov_code == 111) or ('invalid sender id' in prov_msg.lower()):
                    hint = 'Choose another sender name or request approval in Sender Names.'
            return _error_response(
                user_msg,
                status.HTTP_400_BAD_REQUEST,
                error_code='PROVIDER_ERROR',
                detail=beem_error,
                user_hint=hint,
                actions={'request_default_url': '/api/messaging/sender-requests/request-default/', 'available_url': '/api/messaging/sender-requests/available/'}
            )

        # Update SMS message with provider response
        sms_message.provider_response = beem_response.get('response', {})
        sms_message.status = 'sent' if beem_response.get('success') else 'failed'
        sms_message.sent_at = timezone.now()
        sms_message.cost_amount = beem_response.get('cost_estimate', 0.0)
        sms_message.save()

        # Update base message
        base_message.status = 'sent' if beem_response.get('success') else 'failed'
        base_message.sent_at = timezone.now()
        base_message.cost_micro = int(beem_response.get('cost_estimate', 0.0) * 1000000)
        base_message.save()
        
        # Deduct SMS credits after successful send
        if beem_response.get('success'):
            try:
                validation_service.deduct_credits(
                    amount=len(data['recipients']),
                    sender_id=sender_id_obj.sender_id,
                    message_id=str(base_message.id),
                    description=f"Bulk SMS sent to {len(data['recipients'])} recipients"
                )
                logger.info(f"Deducted {len(data['recipients'])} SMS credits for bulk message {base_message.id}")
            except SMSValidationError as e:
                logger.error(f"Failed to deduct credits for bulk message {base_message.id}: {e}")
                # Don't fail the message if credit deduction fails, just log it

        return Response({
            'success': True,
            'message': 'SMS sent successfully via Beem',
            'data': {
                'message_id': str(sms_message.id),
                'base_message_id': str(base_message.id),
                'provider': 'beem',
                'recipient_count': len(data['recipients']),
                'cost_estimate': beem_response.get('cost_estimate', 0.0),
                'status': sms_message.status,
                'beem_response': beem_response
            }
        }, status=status.HTTP_201_CREATED)

    except BeemSMSError as e:
        logger.error(f"Beem SMS error: {str(e)}")
        return _error_response(
            'Your message could not be sent due to provider issues.',
            status.HTTP_400_BAD_REQUEST,
            error_code='PROVIDER_ERROR',
            detail=str(e),
            user_hint='Please wait a moment and try again.'
        )

    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {str(e)}")
        return _error_response(
            'Something went wrong while sending your message.',
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code='SYSTEM_ERROR',
            detail=str(e),
            user_hint='Please try again. If the problem persists, contact support.'
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_bulk_sms(request):
    """
    Send bulk SMS messages via Beem Africa

    POST /api/messaging/sms/send-bulk/

    Request Body:
    {
        "messages": [
            {
                "message": "Hello from Mifumo WMS!",
                "recipients": ["255700000001", "255700000002"],
                "sender_id": "MIFUMO"
            },
            {
                "message": "Another message",
                "recipients": ["255700000003"],
                "sender_id": "MIFUMO"
            }
        ],
        "schedule_time": "2024-01-01T10:00:00Z" // optional
    }
    """
    try:
        serializer = SMSBulkSendSerializer(data=request.data)
        if not serializer.is_valid():
            # Check if the error is related to special characters
            errors = serializer.errors
            has_special_chars = any('special characters' in str(error) for error in errors.get('messages', []))
            
            if has_special_chars:
                return _error_response(
                    'One or more messages contain special characters or emojis that are not allowed.',
                    status.HTTP_400_BAD_REQUEST,
                    error_code='INVALID_CHARACTERS',
                    errors=errors,
                    user_hint='Please use only plain text (letters, numbers, spaces, and basic punctuation). Remove emojis and special characters.',
                    actions={'allowed_chars': 'Letters, numbers, spaces, and basic punctuation only'}
                )
            else:
                return _error_response(
                    'Some information is missing or invalid.',
                    status.HTTP_400_BAD_REQUEST,
                    error_code='VALIDATION_ERROR',
                    errors=errors,
                    user_hint='Check each message block and try again.'
                )

        data = serializer.validated_data
        tenant = request.user.tenant

        # Check if user has a tenant
        if not tenant:
            return _error_response(
                'You are not linked to any organization.',
                status.HTTP_400_BAD_REQUEST,
                error_code='NO_TENANT',
                user_hint='Please contact support to link your account to an organization.'
            )

        # Get Beem provider
        beem_provider = get_or_create_beem_provider(tenant)

        # Initialize Beem service
        beem_service = BeemSMSService()

        results = []
        total_recipients = 0
        total_cost = 0.0

        with transaction.atomic():
            for message_data in data['messages']:
                # Get and validate sender ID
                sender_id = message_data.get('sender_id')
                sender_id_obj = None
                if sender_id:
                    sender_id_obj = get_sender_id(tenant, sender_id)
                if not sender_id_obj:
                    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
                        sender_id_obj = get_or_create_default_sender(tenant, beem_provider)
                    else:
                        if (sender_id or '').strip().lower() == 'taarifa-sms':
                            sender_id_obj = get_or_create_default_sender(tenant, beem_provider)
                        else:
                            return _error_response(
                                'Sender name is missing or not available.',
                                status.HTTP_400_BAD_REQUEST,
                                error_code='SENDER_ID_INVALID',
                                user_hint='Choose an approved sender name or request the default in Sender Names.',
                                actions={'request_default_url': '/api/messaging/sender-requests/request-default/', 'available_url': '/api/messaging/sender-requests/available/'}
                            )

                # Send via Beem
                beem_response = beem_service.send_sms(
                    message=message_data['message'],
                    recipients=message_data['recipients'],
                    source_addr=sender_id_obj.sender_id,
                    schedule_time=data.get('schedule_time'),
                    encoding=message_data.get('encoding', 0)
                )

                # Create message records
                base_message = Message.objects.create(
                    tenant=tenant,
                    conversation=None,
                    direction='out',
                    provider='sms',
                    text=message_data['message'],
                    created_by=request.user
                )

                sms_message = SMSMessage.objects.create(
                    tenant=tenant,
                    base_message=base_message,
                    provider=beem_provider,
                    sender_id=sender_id_obj,
                    status='sent' if beem_response.get('success') else 'failed',
                    provider_response=beem_response.get('response', {}),
                    sent_at=timezone.now(),
                    cost_amount=beem_response.get('cost_estimate', 0.0)
                )

                results.append({
                    'message_id': str(sms_message.id),
                    'recipient_count': len(message_data['recipients']),
                    'status': sms_message.status,
                    'cost': beem_response.get('cost_estimate', 0.0)
                })

                total_recipients += len(message_data['recipients'])
                total_cost += beem_response.get('cost_estimate', 0.0)

        return Response({
            'success': True,
            'message': f'Bulk SMS sent successfully via Beem',
            'data': {
                'total_messages': len(data['messages']),
                'total_recipients': total_recipients,
                'total_cost': round(total_cost, 4),
                'provider': 'beem',
                'results': results
            }
        }, status=status.HTTP_201_CREATED)

    except BeemSMSError as e:
        logger.error(f"Beem bulk SMS error: {str(e)}")
        prov_code, prov_msg = _parse_provider_error(str(e))
        user_msg = 'Your messages could not be sent due to provider issues.'
        hint = 'Please wait a moment and try again.'
        if prov_msg:
            user_msg = f"Provider error: {prov_msg}"
            if (prov_code == 111) or ('invalid sender id' in prov_msg.lower()):
                hint = 'Choose another sender name or request approval in Sender Names.'
        return _error_response(
            user_msg,
            status.HTTP_400_BAD_REQUEST,
            error_code='PROVIDER_ERROR',
            detail=str(e),
            user_hint=hint,
            actions={'request_default_url': '/api/messaging/sender-requests/request-default/', 'available_url': '/api/messaging/sender-requests/available/'}
        )

    except Exception as e:
        logger.error(f"Unexpected error sending bulk SMS: {str(e)}")
        return _error_response(
            'Something went wrong while sending your messages.',
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code='SYSTEM_ERROR',
            detail=str(e),
            user_hint='Please try again. If the problem persists, contact support.'
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_beem_connection(request):
    """
    Test connection to Beem SMS API

    GET /api/messaging/sms/test-beem/

    Response:
    {
        "success": true,
        "message": "Connection test successful",
        "data": {
            "provider": "beem",
            "api_key_configured": true,
            "secret_key_configured": true,
            "connection_status": "success"
        }
    }
    """
    try:
        beem_service = BeemSMSService()
        test_result = beem_service.test_connection()

        return Response({
            'success': test_result.get('success', False),
            'message': test_result.get('message', 'Connection test completed'),
            'data': test_result
        }, status=status.HTTP_200_OK)

    except BeemSMSError as e:
        return Response({
            'success': False,
            'message': f'Beem connection test failed: {str(e)}',
            'data': {
                'provider': 'beem',
                'error': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Connection test error: {str(e)}',
            'data': {
                'provider': 'beem',
                'error': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_beem_balance(request):
    """
    Get Beem account balance

    GET /api/messaging/sms/beem-balance/

    Response:
    {
        "success": true,
        "data": {
            "provider": "beem",
            "balance": "N/A",
            "currency": "USD",
            "message": "Balance check not available via API"
        }
    }
    """
    try:
        beem_service = BeemSMSService()
        balance_info = beem_service.get_account_balance()

        return Response({
            'success': balance_info.get('success', False),
            'data': balance_info
        }, status=status.HTTP_200_OK)

    except BeemSMSError as e:
        return Response({
            'success': False,
            'message': f'Failed to get Beem balance: {str(e)}',
            'data': {
                'provider': 'beem',
                'error': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Balance check error: {str(e)}',
            'data': {
                'provider': 'beem',
                'error': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sms_stats(request):
    """
    Get SMS statistics for the tenant

    GET /api/messaging/sms/stats/

    Response:
    {
        "success": true,
        "data": {
            "total_sent": 1500,
            "total_delivered": 1450,
            "total_failed": 50,
            "delivery_rate": 96.67,
            "this_month_sent": 300,
            "this_month_delivered": 290,
            "this_month_failed": 10,
            "cost_this_month": 7.50
        }
    }
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get SMS statistics for the tenant
        from django.db.models import Count, Sum, Q
        from datetime import datetime, timedelta

        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total statistics
        total_sent = SMSMessage.objects.filter(tenant=tenant).count()
        total_delivered = SMSMessage.objects.filter(tenant=tenant, status='delivered').count()
        total_failed = SMSMessage.objects.filter(tenant=tenant, status='failed').count()

        # This month statistics
        this_month_sent = SMSMessage.objects.filter(
            tenant=tenant,
            created_at__gte=this_month_start
        ).count()
        this_month_delivered = SMSMessage.objects.filter(
            tenant=tenant,
            status='delivered',
            created_at__gte=this_month_start
        ).count()
        this_month_failed = SMSMessage.objects.filter(
            tenant=tenant,
            status='failed',
            created_at__gte=this_month_start
        ).count()

        # Calculate delivery rate
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0

        # Calculate cost (assuming 25 TZS per SMS)
        cost_per_sms = 25  # TZS
        cost_this_month = this_month_sent * cost_per_sms

        return Response({
            'success': True,
            'data': {
                'total_sent': total_sent,
                'total_delivered': total_delivered,
                'total_failed': total_failed,
                'delivery_rate': round(delivery_rate, 2),
                'this_month_sent': this_month_sent,
                'this_month_delivered': this_month_delivered,
                'this_month_failed': this_month_failed,
                'cost_this_month': cost_this_month
            }
        })

    except Exception as e:
        logger.error(f"SMS stats error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve SMS statistics',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sms_delivery_status(request, message_id):
    """
    Get delivery status for SMS message

    GET /api/messaging/sms/{message_id}/status/

    Response:
    {
        "success": true,
        "data": {
            "message_id": "uuid",
            "status": "delivered",
            "provider": "beem",
            "sent_at": "2024-01-01T10:00:00Z",
            "delivered_at": "2024-01-01T10:00:05Z"
        }
    }
    """
    try:
        tenant = request.user.tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        sms_message = get_object_or_404(
            SMSMessage,
            id=message_id,
            tenant=tenant
        )

        # Get status from Beem
        beem_service = BeemSMSService()
        status_info = beem_service.get_delivery_status(str(sms_message.id))

        return Response({
            'success': True,
            'data': {
                'message_id': str(sms_message.id),
                'base_message_id': str(sms_message.base_message.id),
                'status': sms_message.status,
                'provider': 'beem',
                'sent_at': sms_message.sent_at.isoformat() if sms_message.sent_at else None,
                'delivered_at': sms_message.delivered_at.isoformat() if sms_message.delivered_at else None,
                'cost': float(sms_message.cost_amount),
                'beem_status': status_info
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting SMS delivery status: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to get delivery status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_phone_number(request):
    """
    Validate phone number format for Beem SMS

    POST /api/messaging/sms/validate-phone/

    Request Body:
    {
        "phone_number": "255700000001"
    }

    Response:
    {
        "success": true,
        "data": {
            "phone_number": "255700000001",
            "formatted": "255700000001",
            "is_valid": true,
            "provider": "beem"
        }
    }
    """
    try:
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'success': False,
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        beem_service = BeemSMSService()
        is_valid = beem_service.validate_phone_number(phone_number)
        formatted = beem_service._format_phone_number(phone_number)

        return Response({
            'success': True,
            'data': {
                'phone_number': phone_number,
                'formatted': formatted,
                'is_valid': is_valid,
                'provider': 'beem'
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error validating phone number: {str(e)}")
        return Response({
            'success': False,
            'message': f'Phone number validation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper functions

def get_or_create_beem_provider(tenant):
    """Get or create Beem SMS provider for tenant"""
    try:
        # First try to get the default provider
        provider = SMSProvider.objects.filter(
            tenant=tenant,
            provider_type='beem',
            is_active=True,
            is_default=True
        ).first()

        if provider:
            return provider

        # If no default, get the first active provider
        provider = SMSProvider.objects.filter(
            tenant=tenant,
            provider_type='beem',
            is_active=True
        ).first()

        if provider:
            return provider

        # If no provider exists, create one
        raise SMSProvider.DoesNotExist()

    except SMSProvider.DoesNotExist:
        # Create default Beem provider
        provider = SMSProvider.objects.create(
            tenant=tenant,
            name='Beem Africa SMS',
            provider_type='beem',
            api_key='',  # Will be set from environment
            secret_key='',  # Will be set from environment
            api_url='https://apisms.beem.africa/v1/send',
            is_active=True,
            is_default=True,
            cost_per_sms=0.05,
            currency='USD'
        )
        return provider


def get_sender_id(tenant, sender_id_name):
    """Get and validate SMS sender ID for tenant"""
    if not sender_id_name:
        return None

    try:
        return SMSSenderID.objects.get(
            tenant=tenant,
            sender_id=sender_id_name,
            status='active'
        )
    except SMSSenderID.DoesNotExist:
        return None


def get_or_create_default_sender(tenant, provider):
    """Ensure default sender 'Taarifa-SMS' exists and is active for the tenant."""
    sender = SMSSenderID.objects.filter(
        tenant=tenant,
        sender_id='Taarifa-SMS'
    ).first()
    if sender:
        if sender.status != 'active' or sender.provider_id != provider.id:
            sender.status = 'active'
            sender.provider = provider
            sender.save()
        return sender

    return SMSSenderID.objects.create(
        tenant=tenant,
        provider=provider,
        sender_id='Taarifa-SMS',
        status='active',
        sample_content='A test use case for the sender name purposely used for information transfer.'
    )
