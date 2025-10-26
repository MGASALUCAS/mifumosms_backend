"""
Simple SMS Aggregator API - Working version
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import APIAccount, APIKey
from .utils import format_api_response, generate_account_id_string
from messaging.services.sms_service import SMSService
from messaging.models import Message
from accounts.models import User
from tenants.models import Tenant


@api_view(['POST'])
@permission_classes([AllowAny])
def register_sms_aggregator_user(request):
    """Register a new SMS Aggregator user."""
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
                'first_name': request.data.get('contact_name', 'SMS Aggregator'),
                'last_name': request.data.get('company_name', ''),
                'phone_number': request.data['contact_phone'],
                'is_active': True,
                'is_verified': True
            }
        )
        
        if not created:
            return Response(format_api_response(
                success=False,
                message="Email already registered",
                error_code="EMAIL_EXISTS"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create tenant for SMS aggregators
        import uuid
        
        # Create unique subdomain
        company_slug = request.data['company_name'].lower().replace(' ', '-').replace('_', '-')
        subdomain = f"agg-{company_slug}-{str(uuid.uuid4())[:8]}"
        
        tenant, _ = Tenant.objects.get_or_create(
            name=f"SMS Aggregator - {request.data['company_name']}",
            defaults={
                'subdomain': subdomain,
                'business_name': request.data['company_name'],
                'business_type': request.data.get('business_type', 'SMS Aggregator'),
                'email': request.data['contact_email'],
                'phone_number': request.data['contact_phone'],
                'is_active': True
            }
        )
        
        # Create API account with higher limits for aggregators
        with transaction.atomic():
            api_account = APIAccount.objects.create(
                account_id=generate_account_id_string(),
                name=request.data['company_name'],
                description=request.data.get('description', 'SMS Aggregator Integration'),
                owner=user,
                tenant=tenant,
                rate_limit_per_minute=500,  # Higher limits for aggregators
                rate_limit_per_hour=5000,
                rate_limit_per_day=50000
            )
            
            # Create API key
            api_key = APIKey.objects.create(
                api_account=api_account
            )
        
        return Response(format_api_response(
            success=True,
            data={
                'user_id': str(user.id),
                'account_id': api_account.account_id,
                'api_key': api_key.key,
                'company_name': request.data['company_name'],
                'rate_limits': {
                    'per_minute': api_account.rate_limit_per_minute,
                    'per_hour': api_account.rate_limit_per_hour,
                    'per_day': api_account.rate_limit_per_day
                }
            },
            message="SMS Aggregator registered successfully"
        ), status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Registration failed",
            error_code="REGISTRATION_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_aggregated_sms(request):
    """Send SMS through the aggregator service."""
    # Simple API key validation
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    try:
        api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
        api_account = api_key_obj.api_account
    except APIKey.DoesNotExist:
        return Response(format_api_response(
            success=False,
            message="Invalid API key",
            error_code="INVALID_API_KEY"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
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
        # Use the existing SMS service
        sms_service = SMSService(str(api_account.tenant.id))
        
        # Normalize phone number
        to_number = request.data['to']
        if to_number.startswith('+'):
            to_number = to_number[1:]
        
        # Send SMS
        result = sms_service.send_sms(
            to=to_number,
            message=request.data['message'],
            sender_id=request.data.get('sender_id', 'Taarifa-SMS'),
            recipient_id=f"agg_{api_account.account_id}_{int(timezone.now().timestamp())}"
        )
        
        if result.get('success'):
            # Create message record
            message_obj = Message.objects.create(
                tenant_id=api_account.tenant.id,
                to_number=f"+{to_number}",
                text=request.data['message'],
                direction='outbound',
                status='sent',
                provider='beem_africa',
                created_by_id=api_account.owner.id
            )
            
            # Log usage
            from .models import APIUsageLog
            APIUsageLog.objects.create(
                api_account=api_account,
                api_key=api_key_obj,
                endpoint=request.path,
                method=request.method,
                status_code=200,
                request_ip=request.META.get('REMOTE_ADDR'),
                sms_message_id=str(message_obj.id),
                sms_recipient=f"+{to_number}",
                sms_status="SENT"
            )
            
            return Response(format_api_response(
                success=True,
                data={
                    'message_id': str(message_obj.id),
                    'user_id': str(api_account.owner.id),
                    'to': f"+{to_number}",
                    'message': request.data['message'],
                    'status': 'sent',
                    'delivery_status': 'pending',
                    'provider': 'beem_africa',
                    'sent_at': timezone.now().isoformat()
                },
                message="SMS sent successfully through aggregator"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="SMS sending failed",
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
def get_network_coverage(request):
    """Get network coverage information."""
    try:
        coverage = {
            'countries': ['Tanzania', 'Kenya', 'Uganda', 'Rwanda'],
            'networks': {
                'Tanzania': ['vodacom', 'airtel', 'tiGo', 'halotel', 'zantel'],
                'Kenya': ['safaricom', 'airtel', 'telkom'],
                'Uganda': ['mtn', 'airtel', 'utl'],
                'Rwanda': ['mtn', 'airtel']
            },
            'providers': ['beem_africa', 'africas_talking', 'twilio'],
            'total_networks': 12
        }
        
        return Response(format_api_response(
            success=True,
            data=coverage,
            message="Network coverage information retrieved successfully"
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
def get_message_status(request, message_id):
    """Get message delivery status."""
    try:
        message = Message.objects.get(id=message_id)
        
        return Response(format_api_response(
            success=True,
            data={
                'message_id': str(message.id),
                'to': message.to_number,
                'message': message.text,
                'status': message.status,
                'delivery_status': message.status,
                'provider': 'beem_africa',
                'sent_at': message.created_at.isoformat() if message.created_at else None,
                'delivered_at': getattr(message, 'delivered_at', None).isoformat() if getattr(message, 'delivered_at', None) else None
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
    """Get delivery reports."""
    try:
        messages = Message.objects.filter(
            direction='outbound'
        ).order_by('-created_at')[:50]
        
        reports = []
        for msg in messages:
            reports.append({
                'message_id': str(msg.id),
                'to': msg.to_number,
                'message': msg.text,
                'status': msg.status,
                'provider': 'beem_africa',
                'sent_at': msg.created_at.isoformat() if msg.created_at else None,
                'delivered_at': getattr(msg, 'delivered_at', None).isoformat() if getattr(msg, 'delivered_at', None) else None
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'reports': reports,
                'total': len(reports),
                'limit': 50
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
    """Get API information."""
    try:
        info = {
            'name': 'SMS Aggregator API',
            'version': '1.0.0',
            'description': 'Multi-network SMS aggregation service for African markets',
            'features': [
                'Multi-network SMS routing',
                'Automatic network detection',
                'Delivery tracking and reports',
                'Compliance checking',
                'Cost optimization',
                'Reliability and failover'
            ],
            'supported_countries': ['Tanzania', 'Kenya', 'Uganda', 'Rwanda'],
            'providers': ['beem_africa', 'africas_talking', 'twilio'],
            'rate_limits': {
                'per_minute': 500,
                'per_hour': 5000,
                'per_day': 50000
            }
        }
        
        return Response(format_api_response(
            success=True,
            data=info,
            message="API information retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

