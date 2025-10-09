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
from .services.beem_sms import BeemSMSService, BeemSMSError
from .serializers_sms_beem import (
    SMSSendSerializer, 
    SMSBulkSendSerializer, 
    SMSScheduleSerializer,
    SMSMessageSerializer,
    SMSDeliveryReportSerializer
)

logger = logging.getLogger(__name__)


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
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        tenant = request.user.tenant
        
        # Check if user has a tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create Beem provider
        beem_provider = get_or_create_beem_provider(tenant)
        
        # Get and validate sender ID
        sender_id = data.get('sender_id')
        if not sender_id:
            return Response({
                'success': False,
                'message': 'Sender ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sender_id_obj = get_sender_id(tenant, sender_id)
        if not sender_id_obj:
            return Response({
                'success': False,
                'message': f'Sender ID "{sender_id}" is not registered or not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get template if provided
        template = None
        if data.get('template_id'):
            template = get_object_or_404(SMSTemplate, id=data['template_id'], tenant=tenant)
            message_content = template.message
        else:
            message_content = data['message']
        
        # Initialize Beem service
        beem_service = BeemSMSService()
        
        # Send SMS via Beem
        with transaction.atomic():
            # Create base message
            base_message = Message.objects.create(
                tenant=tenant,
                conversation=None,  # SMS doesn't use conversations
                direction='out',
                provider='sms',
                text=message_content,
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
            
            # Send via Beem API
            beem_response = beem_service.send_sms(
                message=message_content,
                recipients=data['recipients'],
                source_addr=sender_id_obj.sender_id,
                schedule_time=data.get('schedule_time'),
                encoding=data.get('encoding', 0)
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
        return Response({
            'success': False,
            'message': f'SMS sending failed: {str(e)}',
            'provider': 'beem'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {str(e)}")
        return Response({
            'success': False,
            'message': 'An unexpected error occurred while sending SMS',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        tenant = request.user.tenant
        
        # Check if user has a tenant
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
                if not sender_id:
                    return Response({
                        'success': False,
                        'message': 'Sender ID is required for all messages'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                sender_id_obj = get_sender_id(tenant, sender_id)
                if not sender_id_obj:
                    return Response({
                        'success': False,
                        'message': f'Sender ID "{sender_id}" is not registered or not active'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
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
        return Response({
            'success': False,
            'message': f'Bulk SMS sending failed: {str(e)}',
            'provider': 'beem'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected error sending bulk SMS: {str(e)}")
        return Response({
            'success': False,
            'message': 'An unexpected error occurred while sending bulk SMS',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        provider = SMSProvider.objects.get(
            tenant=tenant, 
            provider_type='beem',
            is_active=True
        )
        return provider
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
