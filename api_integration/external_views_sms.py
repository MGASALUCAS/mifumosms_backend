"""
External SMS API views for integrations.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .views import ExternalAPIViewMixin
from .utils import format_api_response, get_client_ip
from messaging.services.sms_service import SMSService
from messaging.models import Message, Contact
from accounts.services.sms_verification import SMSVerificationService


@api_view(['POST'])
def send_sms(request):
    """Send SMS message."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    required_fields = ['to', 'message']
    for field in required_fields:
        if field not in request.data:
            return Response(format_api_response(
                success=False,
                message=f"Missing required field: {field}"
            ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get SMS service
        sms_service = SMSService(str(account.tenant.id))
        
        # Send SMS
        result = sms_service.send_sms(
            to=request.data['to'],
            message=request.data['message'],
            sender_id=request.data.get('sender_id', 'Taarifa-SMS'),
            recipient_id=request.data.get('recipient_id', f"api_{int(timezone.now().timestamp())}")
        )
        
        if result.get('success'):
            # Create message record
            message = Message.objects.create(
                tenant=account.tenant,
                to_number=request.data['to'],
                text=request.data['message'],
                direction='outbound',
                status='sent',
                provider='beem',
                created_by=account.owner
            )
            
            return Response(format_api_response(
                success=True,
                data={
                    'message_id': str(message.id),
                    'to': request.data['to'],
                    'message': request.data['message'],
                    'status': 'sent',
                    'provider_response': result
                },
                message="SMS sent successfully"
            ))
        else:
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


@api_view(['POST'])
def send_bulk_sms(request):
    """Send bulk SMS messages."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    if 'messages' not in request.data:
        return Response(format_api_response(
            success=False,
            message="Missing required field: messages"
        ), status=status.HTTP_400_BAD_REQUEST)
    
    messages = request.data['messages']
    if not isinstance(messages, list):
        return Response(format_api_response(
            success=False,
            message="Messages must be a list"
        ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get SMS service
        sms_service = SMSService(str(account.tenant.id))
        
        results = []
        successful = 0
        failed = 0
        
        for i, msg_data in enumerate(messages):
            if 'to' not in msg_data or 'message' not in msg_data:
                results.append({
                    'index': i,
                    'success': False,
                    'error': 'Missing required fields: to, message'
                })
                failed += 1
                continue
            
            try:
                # Send SMS
                result = sms_service.send_sms(
                    to=msg_data['to'],
                    message=msg_data['message'],
                    sender_id=msg_data.get('sender_id', 'Taarifa-SMS'),
                    recipient_id=msg_data.get('recipient_id', f"api_bulk_{i}_{int(timezone.now().timestamp())}")
                )
                
                if result.get('success'):
                    # Create message record
                    message = Message.objects.create(
                        tenant=account.tenant,
                        to_number=msg_data['to'],
                        text=msg_data['message'],
                        direction='outbound',
                        status='sent',
                        provider='beem',
                        created_by=account.owner
                    )
                    
                    results.append({
                        'index': i,
                        'success': True,
                        'message_id': str(message.id),
                        'to': msg_data['to']
                    })
                    successful += 1
                else:
                    results.append({
                        'index': i,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                    failed += 1
                    
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'error': str(e)
                })
                failed += 1
        
        return Response(format_api_response(
            success=True,
            data={
                'total': len(messages),
                'successful': successful,
                'failed': failed,
                'results': results
            },
            message=f"Bulk SMS processing completed: {successful} successful, {failed} failed"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_sms_status(request, message_id):
    """Get SMS message status."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get message
        message = get_object_or_404(
            Message,
            id=message_id,
            tenant=account.tenant
        )
        
        return Response(format_api_response(
            success=True,
            data={
                'message_id': str(message.id),
                'to': message.to_number,
                'text': message.text,
                'status': message.status,
                'direction': message.direction,
                'provider': message.provider,
                'created_at': message.created_at.isoformat(),
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None
            },
            message="SMS status retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_sms_history(request):
    """Get SMS message history."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')
        to_filter = request.GET.get('to')
        
        # Build query
        messages = Message.objects.filter(tenant=account.tenant)
        
        if status_filter:
            messages = messages.filter(status=status_filter)
        
        if to_filter:
            messages = messages.filter(to_number__icontains=to_filter)
        
        # Apply pagination
        total = messages.count()
        messages = messages.order_by('-created_at')[offset:offset + limit]
        
        # Format response
        message_list = []
        for message in messages:
            message_list.append({
                'message_id': str(message.id),
                'to': message.to_number,
                'text': message.text,
                'status': message.status,
                'direction': message.direction,
                'provider': message.provider,
                'created_at': message.created_at.isoformat(),
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'messages': message_list,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total
                }
            },
            message="SMS history retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_verification_sms(request):
    """Send SMS verification code."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    if 'phone_number' not in request.data:
        return Response(format_api_response(
            success=False,
            message="Missing required field: phone_number"
        ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get SMS verification service
        sms_verification = SMSVerificationService(str(account.tenant.id))
        
        # Send verification code
        result = sms_verification.send_verification_sms(
            phone_number=request.data['phone_number'],
            code=request.data.get('code'),  # Optional custom code
            message_type=request.data.get('message_type', 'verification')
        )
        
        if result.get('success'):
            return Response(format_api_response(
                success=True,
                data={
                    'phone_number': result.get('phone_number'),
                    'message': 'Verification code sent successfully'
                },
                message="Verification SMS sent successfully"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="Failed to send verification SMS",
                error_code="VERIFICATION_SEND_FAILED",
                details=result.get('error', 'Unknown error')
            ), status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_sms_code(request):
    """Verify SMS verification code."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    required_fields = ['phone_number', 'code']
    for field in required_fields:
        if field not in request.data:
            return Response(format_api_response(
                success=False,
                message=f"Missing required field: {field}"
            ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get SMS verification service
        sms_verification = SMSVerificationService(str(account.tenant.id))
        
        # Verify code
        result = sms_verification.verify_code(
            phone_number=request.data['phone_number'],
            code=request.data['code']
        )
        
        if result.get('success'):
            return Response(format_api_response(
                success=True,
                data={
                    'phone_number': request.data['phone_number'],
                    'verified': True
                },
                message="SMS code verified successfully"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="Invalid verification code",
                error_code="VERIFICATION_FAILED",
                details=result.get('error', 'Invalid code')
            ), status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_sender_ids(request):
    """Get available sender IDs."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get SMS service
        sms_service = SMSService(str(account.tenant.id))
        
        # Get sender IDs
        result = sms_service.get_sender_ids()
        
        if result.get('success'):
            return Response(format_api_response(
                success=True,
                data={
                    'sender_ids': result.get('sender_ids', [])
                },
                message="Sender IDs retrieved successfully"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="Failed to retrieve sender IDs",
                error_code="SENDER_IDS_FAILED",
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
def get_sender_status(request, sender_id):
    """Get sender ID status."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get SMS service
        sms_service = SMSService(str(account.tenant.id))
        
        # Get sender ID status
        result = sms_service.get_sender_id_status(sender_id)
        
        if result.get('success'):
            return Response(format_api_response(
                success=True,
                data={
                    'sender_id': sender_id,
                    'status': result.get('status', 'unknown')
                },
                message="Sender ID status retrieved successfully"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="Failed to retrieve sender ID status",
                error_code="SENDER_STATUS_FAILED",
                details=result.get('error', 'Unknown error')
            ), status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)






