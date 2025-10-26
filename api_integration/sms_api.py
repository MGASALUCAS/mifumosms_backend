"""
SMS API implementation following African's Talking and Beem Africa patterns.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import uuid
import json

from .models import APIAccount, APIKey, APIUsageLog
from .authentication import APIKeyAuthentication
from .utils import format_api_response, get_client_ip, log_api_usage
from messaging.services.sms_service import SMSService
from messaging.models import Message, Contact
from tenants.models import Tenant


@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms(request):
    """
    Send SMS message to one or more recipients.
    
    Similar to African's Talking SMS API:
    - POST /messaging/v1/send
    - Beem Africa SMS API
    
    Request Body:
    {
        "message": "Hello from Mifumo SMS!",
        "recipients": ["+255123456789", "+255987654321"],
        "sender_id": "MIFUMO",
        "schedule_time": "2024-01-01T10:00:00Z"  // Optional
    }
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Authentication required",
            error_code="AUTHENTICATION_REQUIRED"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Validate API key
    from .utils import validate_api_credentials
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Check permissions
    if 'write' not in api_key_obj.permissions:
        return Response(format_api_response(
            success=False,
            message="Insufficient permissions",
            error_code="INSUFFICIENT_PERMISSIONS"
        ), status=status.HTTP_403_FORBIDDEN)
    
    # Validate request data
    try:
        message_text = request.data.get('message', '').strip()
        recipients = request.data.get('recipients', [])
        sender_id = request.data.get('sender_id', 'Taarifa-SMS')
        schedule_time = request.data.get('schedule_time')
        
        if not message_text:
            return Response(format_api_response(
                success=False,
                message="Message text is required",
                error_code="MISSING_MESSAGE"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        if not recipients or not isinstance(recipients, list):
            return Response(format_api_response(
                success=False,
                message="Recipients list is required",
                error_code="MISSING_RECIPIENTS"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone numbers
        valid_recipients = []
        for phone in recipients:
            if isinstance(phone, str) and phone.startswith('+'):
                valid_recipients.append(phone)
            else:
                return Response(format_api_response(
                    success=False,
                    message=f"Invalid phone number format: {phone}",
                    error_code="INVALID_PHONE_FORMAT"
                ), status=status.HTTP_400_BAD_REQUEST)
        
        if not valid_recipients:
            return Response(format_api_response(
                success=False,
                message="No valid recipients found",
                error_code="NO_VALID_RECIPIENTS"
            ), status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Invalid request data",
            error_code="INVALID_REQUEST_DATA",
            details=str(e)
        ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get SMS service
        sms_service = SMSService(str(api_key_obj.api_account.tenant.id))
        
        # Send SMS
        result = sms_service.send_sms(
            message=message_text,
            recipients=valid_recipients,
            source_addr=sender_id,
            schedule_time=schedule_time
        )
        
        if result.get('success'):
            # Create message record
            message_id = str(uuid.uuid4())
            
            with transaction.atomic():
                message = Message.objects.create(
                    id=message_id,
                    tenant=api_key_obj.api_account.tenant,
                    content=message_text,
                    recipient_count=len(valid_recipients),
                    status='sent',
                    created_by=api_key_obj.api_account.owner,
                    sender_id=sender_id
                )
                
                # Log API usage
                log_api_usage(
                    api_account=api_key_obj.api_account,
                    api_key=api_key_obj,
                    integration=None,
                    endpoint=request.path,
                    method=request.method,
                    status_code=200,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_size=len(request.body) if hasattr(request, 'body') else 0,
                    response_size=len(str(result)),
                    response_time_ms=0,  # Will be calculated by middleware
                    error_message=""
                )
            
            return Response(format_api_response(
                success=True,
                data={
                    'message_id': message_id,
                    'recipients': valid_recipients,
                    'cost': result.get('cost_estimate', 0.0),
                    'currency': 'USD',
                    'provider': result.get('provider', 'unknown'),
                    'status': 'sent'
                },
                message="SMS sent successfully"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message=result.get('error', 'Failed to send SMS'),
                error_code="SMS_SEND_FAILED",
                details=result
            ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_message_status(request, message_id):
    """
    Get delivery status of a sent message.
    
    Similar to African's Talking:
    - GET /messaging/v1/status/{messageId}
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Authentication required",
            error_code="AUTHENTICATION_REQUIRED"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
    from .utils import validate_api_credentials
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get message
        message = Message.objects.get(
            id=message_id,
            tenant=api_key_obj.api_account.tenant
        )
        
        # Get delivery status
        status_data = {
            'message_id': str(message.id),
            'status': message.status,
            'created_at': message.created_at.isoformat(),
            'updated_at': message.updated_at.isoformat(),
            'recipient_count': message.recipient_count,
            'content': message.content[:100] + '...' if len(message.content) > 100 else message.content,
            'sender_id': message.sender_id
        }
        
        # Add delivery details if available
        if hasattr(message, 'delivery_logs'):
            delivery_logs = message.delivery_logs.all()
            status_data['delivery_details'] = [
                {
                    'recipient': log.recipient,
                    'status': log.status,
                    'delivered_at': log.delivered_at.isoformat() if log.delivered_at else None,
                    'error_message': log.error_message
                }
                for log in delivery_logs
            ]
        
        return Response(format_api_response(
            success=True,
            data=status_data,
            message="Message status retrieved successfully"
        ))
        
    except Message.DoesNotExist:
        return Response(format_api_response(
            success=False,
            message="Message not found",
            error_code="MESSAGE_NOT_FOUND"
        ), status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_delivery_reports(request):
    """
    Get delivery reports for messages.
    
    Similar to African's Talking:
    - GET /messaging/v1/delivery-reports
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Authentication required",
            error_code="AUTHENTICATION_REQUIRED"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
    from .utils import validate_api_credentials
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        
        # Build query
        messages = Message.objects.filter(tenant=api_key_obj.api_account.tenant)
        
        if start_date:
            messages = messages.filter(created_at__gte=start_date)
        if end_date:
            messages = messages.filter(created_at__lte=end_date)
        if status_filter:
            messages = messages.filter(status=status_filter)
        
        # Pagination
        total = messages.count()
        start = (page - 1) * per_page
        end = start + per_page
        messages = messages.order_by('-created_at')[start:end]
        
        # Format response
        reports = []
        for message in messages:
            reports.append({
                'message_id': str(message.id),
                'status': message.status,
                'created_at': message.created_at.isoformat(),
                'recipient_count': message.recipient_count,
                'content_preview': message.content[:100] + '...' if len(message.content) > 100 else message.content,
                'sender_id': message.sender_id
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'reports': reports,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            },
            message="Delivery reports retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_balance(request):
    """
    Get account balance and credit information.
    
    Similar to African's Talking:
    - GET /user/balance
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Authentication required",
            error_code="AUTHENTICATION_REQUIRED"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
    from .utils import validate_api_credentials
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get tenant billing info
        tenant = api_key_obj.api_account.tenant
        
        # Calculate balance (this would integrate with your billing system)
        balance_data = {
            'account_id': api_key_obj.api_account.account_id,
            'balance': 100.00,  # This would come from billing system
            'currency': 'USD',
            'last_updated': timezone.now().isoformat()
        }
        
        return Response(format_api_response(
            success=True,
            data=balance_data,
            message="Balance retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
