"""
SMS Provider API - Simple integration for external users.
This provides a clean API for users to integrate SMS sending into their applications.
"""
import time
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .models import APIAccount, APIKey
from .utils import format_api_response, get_client_ip, validate_api_credentials
from messaging.services.sms_service import SMSService
from messaging.models import Message
from accounts.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register_sms_provider(request):
    """
    Register a new SMS provider user.
    This creates an API account and generates API credentials.
    """
    try:
        # Validate required fields
        required_fields = ['company_name', 'contact_email', 'contact_phone']
        for field in required_fields:
            if field not in request.data:
                return Response(format_api_response(
                    success=False,
                    message=f"Missing required field: {field}",
                    error_code="MISSING_FIELD"
                ), status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=request.data['contact_email'],
            defaults={
                'first_name': request.data.get('contact_name', 'SMS Provider'),
                'last_name': request.data.get('company_name', ''),
                'phone_number': request.data['contact_phone'],
                'is_active': True,
                'is_verified': True  # Auto-verify SMS providers
            }
        )
        
        if not created:
            return Response(format_api_response(
                success=False,
                message="Email already registered",
                error_code="EMAIL_EXISTS"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create tenant for SMS providers
        from tenants.models import Tenant
        import uuid
        
        # Create unique subdomain
        company_slug = request.data['company_name'].lower().replace(' ', '-').replace('_', '-')
        subdomain = f"sms-{company_slug}-{str(uuid.uuid4())[:8]}"
        
        tenant, _ = Tenant.objects.get_or_create(
            name=f"SMS Provider - {request.data['company_name']}",
            defaults={
                'subdomain': subdomain,
                'business_name': request.data['company_name'],
                'business_type': request.data.get('business_type', 'SMS Provider'),
                'email': request.data['contact_email'],
                'phone_number': request.data['contact_phone'],
                'is_active': True
            }
        )
        
        # Create API account
        with transaction.atomic():
            api_account = APIAccount.objects.create(
                account_id=generate_account_id(),
                name=request.data['company_name'],
                description=request.data.get('description', 'SMS Provider Integration'),
                owner=user,
                tenant=tenant,
                rate_limit_per_minute=100,  # Default limits
                rate_limit_per_hour=1000,
                rate_limit_per_day=10000
            )
            
            # Create API key
            api_key = APIKey.objects.create(
                api_account=api_account,
                key_name="Primary API Key",
                permissions={
                    'sms_send': True,
                    'sms_status': True,
                    'sms_history': True
                }
            )
            api_key.generate_keys()
            api_key.save()
        
        return Response(format_api_response(
            success=True,
            data={
                'user_id': str(user.id),
                'account_id': api_account.account_id,
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
                'company_name': request.data['company_name'],
                'rate_limits': {
                    'per_minute': api_account.rate_limit_per_minute,
                    'per_hour': api_account.rate_limit_per_hour,
                    'per_day': api_account.rate_limit_per_day
                }
            },
            message="SMS Provider registered successfully"
        ), status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Registration failed",
            error_code="REGISTRATION_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def generate_account_id():
    """Generate unique account ID."""
    import secrets
    return f"SP_{secrets.token_urlsafe(12).upper()}"


@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms(request):
    """
    Send SMS message.
    Requires: API Key in Authorization header
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Validate API key
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Check rate limiting
    if api_key_obj.api_account.is_rate_limited('minute'):
        return Response(format_api_response(
            success=False,
            message="Rate limit exceeded (per minute)",
            error_code="RATE_LIMIT_EXCEEDED"
        ), status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Validate request data
    required_fields = ['to', 'message']
    for field in required_fields:
        if field not in request.data:
            return Response(format_api_response(
                success=False,
                message=f"Missing required field: {field}",
                error_code="MISSING_FIELD"
            ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_time = time.time()
        
        # Get SMS service
        sms_service = SMSService(str(api_key_obj.api_account.tenant.id))
        
        # Send SMS
        result = sms_service.send_sms(
            to=request.data['to'],
            message=request.data['message'],
            sender_id=request.data.get('sender_id', 'Taarifa-SMS'),
            recipient_id=f"api_{int(timezone.now().timestamp())}"
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if result.get('success'):
            # Create message record
            message = Message.objects.create(
                tenant=api_key_obj.api_account.tenant,
                to_number=request.data['to'],
                text=request.data['message'],
                direction='outbound',
                status='sent',
                provider='beem',
                created_by=api_key_obj.api_account.owner
            )
            
            # Log usage
            from .utils import log_api_usage
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
                response_size=200,  # Approximate
                response_time_ms=response_time_ms
            )
            
            return Response(format_api_response(
                success=True,
                data={
                    'message_id': str(message.id),
                    'user_id': str(api_key_obj.api_account.owner.id),
                    'to': request.data['to'],
                    'message': request.data['message'],
                    'status': 'sent',
                    'delivery_status': 'pending',
                    'sent_at': message.created_at.isoformat(),
                    'response_time_ms': response_time_ms
                },
                message="SMS sent successfully"
            ))
        else:
            # Log failed attempt
            from .utils import log_api_usage
            log_api_usage(
                api_account=api_key_obj.api_account,
                api_key=api_key_obj,
                integration=None,
                endpoint=request.path,
                method=request.method,
                status_code=400,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_size=len(request.body) if hasattr(request, 'body') else 0,
                response_size=100,
                response_time_ms=response_time_ms,
                error_message=result.get('error', 'SMS send failed')
            )
            
            return Response(format_api_response(
                success=False,
                message="Failed to send SMS",
                error_code="SMS_SEND_FAILED",
                details=result.get('error', 'Unknown error')
            ), status=status.HTTP_400_BAD_REQUEST)
            
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
    Get SMS message delivery status.
    Requires: API Key in Authorization header
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
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
        
        # Determine delivery status
        delivery_status = 'pending'
        if message.status == 'delivered':
            delivery_status = 'delivered'
        elif message.status == 'failed':
            delivery_status = 'failed'
        elif message.status == 'sent':
            delivery_status = 'sent'
        
        return Response(format_api_response(
            success=True,
            data={
                'message_id': str(message.id),
                'user_id': str(api_key_obj.api_account.owner.id),
                'to': message.to_number,
                'message': message.text,
                'status': message.status,
                'delivery_status': delivery_status,
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
                'error_message': message.error_message if hasattr(message, 'error_message') else None
            },
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
    Requires: API Key in Authorization header
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        # Build query
        messages = Message.objects.filter(tenant=api_key_obj.api_account.tenant)
        
        if status_filter:
            messages = messages.filter(status=status_filter)
        
        if from_date:
            messages = messages.filter(created_at__gte=from_date)
        
        if to_date:
            messages = messages.filter(created_at__lte=to_date)
        
        # Apply pagination
        total = messages.count()
        messages = messages.order_by('-created_at')[offset:offset + limit]
        
        # Format response
        reports = []
        for message in messages:
            delivery_status = 'pending'
            if message.status == 'delivered':
                delivery_status = 'delivered'
            elif message.status == 'failed':
                delivery_status = 'failed'
            elif message.status == 'sent':
                delivery_status = 'sent'
            
            reports.append({
                'message_id': str(message.id),
                'user_id': str(api_key_obj.api_account.owner.id),
                'to': message.to_number,
                'message': message.text,
                'status': message.status,
                'delivery_status': delivery_status,
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
                'error_message': message.error_message if hasattr(message, 'error_message') else None
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'reports': reports,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total
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
def get_api_info(request):
    """
    Get API information and account details.
    Requires: API Key in Authorization header
    """
    # Authenticate using API key
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Validate API key
    is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
    if not is_valid:
        return Response(format_api_response(
            success=False,
            message=error_message or "Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get rate limit info
        from .utils import get_rate_limit_info
        rate_limit_info = get_rate_limit_info(api_key_obj.api_account)
        
        return Response(format_api_response(
            success=True,
            data={
                'user_id': str(api_key_obj.api_account.owner.id),
                'account_id': api_key_obj.api_account.account_id,
                'company_name': api_key_obj.api_account.name,
                'api_key': api_key_obj.api_key,
                'rate_limits': rate_limit_info,
                'total_sms_sent': api_key_obj.api_account.total_api_calls,
                'account_status': api_key_obj.api_account.status,
                'api_version': '1.0.0',
                'endpoints': {
                    'send_sms': '/api/sms-provider/send/',
                    'message_status': '/api/sms-provider/status/{message_id}/',
                    'delivery_reports': '/api/sms-provider/reports/',
                    'api_info': '/api/sms-provider/info/'
                }
            },
            message="API information retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
