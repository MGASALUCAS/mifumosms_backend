"""
SMS Aggregator Service - Gateway between applications and African mobile networks.
This service provides multi-network SMS routing, delivery tracking, and compliance handling.
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
from .utils import format_api_response, generate_account_id_string
from messaging.services.sms_service import SMSService
from messaging.models import Message
from accounts.models import User


class SMSAggregatorService:
    """
    SMS Aggregator Service that routes SMS to appropriate African mobile networks.
    """
    
    # African mobile network mappings
    NETWORK_MAPPINGS = {
        # East Africa
        'Tanzania': {
            'vodacom': ['25561', '25562', '25563', '25564', '25565', '25566', '25567', '25568', '25569'],
            'airtel': ['25571', '25572', '25573', '25574', '25575', '25576', '25577', '25578'],
            'tiGo': ['25565', '25566', '25567', '25568', '25569'],
            'halotel': ['25568', '25569'],
            'zantel': ['25577', '25578']
        },
        'Kenya': {
            'safaricom': ['25470', '25471', '25472', '25473', '25474', '25475', '25476', '25477', '25478', '25479'],
            'airtel': ['25470', '25471', '25472', '25473', '25474', '25475', '25476', '25477', '25478', '25479'],
            'telkom': ['25470', '25471', '25472', '25473', '25474', '25475', '25476', '25477', '25478', '25479']
        },
        'Uganda': {
            'mtn': ['25670', '25671', '25672', '25673', '25674', '25675', '25676', '25677', '25678', '25679'],
            'airtel': ['25670', '25671', '25672', '25673', '25674', '25675', '25676', '25677', '25678', '25679'],
            'utl': ['25670', '25671', '25672', '25673', '25674', '25675', '25676', '25677', '25678', '25679']
        },
        'Rwanda': {
            'mtn': ['25070', '25071', '25072', '25073', '25074', '25075', '25076', '25077', '25078', '25079'],
            'airtel': ['25070', '25071', '25072', '25073', '25074', '25075', '25076', '25077', '25078', '25079']
        }
    }
    
    # SMS Provider configurations
    SMS_PROVIDERS = {
        'beem_africa': {
            'name': 'Beem Africa',
            'priority': 1,
            'countries': ['Tanzania', 'Kenya', 'Uganda', 'Rwanda'],
            'reliability': 0.95,
            'cost_per_sms': 0.025
        },
        'africas_talking': {
            'name': 'Africa\'s Talking',
            'priority': 2,
            'countries': ['Tanzania', 'Kenya', 'Uganda', 'Rwanda'],
            'reliability': 0.92,
            'cost_per_sms': 0.023
        },
        'twilio': {
            'name': 'Twilio',
            'priority': 3,
            'countries': ['Tanzania', 'Kenya', 'Uganda', 'Rwanda'],
            'reliability': 0.98,
            'cost_per_sms': 0.030
        }
    }
    
    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.primary_provider = 'beem_africa'
        self.fallback_providers = ['africas_talking', 'twilio']
    
    def detect_network(self, phone_number):
        """
        Detect the mobile network for a given phone number.
        
        Args:
            phone_number (str): Phone number in international format
            
        Returns:
            dict: Network information
        """
        # Normalize phone number
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Extract country code and network prefix
        if phone_number.startswith('255'):
            country = 'Tanzania'
            prefix = phone_number[:5]  # 25561, 25571, etc.
        elif phone_number.startswith('254'):
            country = 'Kenya'
            prefix = phone_number[:5]  # 25470, 25471, etc.
        elif phone_number.startswith('256'):
            country = 'Uganda'
            prefix = phone_number[:5]  # 25670, 25671, etc.
        elif phone_number.startswith('250'):
            country = 'Rwanda'
            prefix = phone_number[:5]  # 25070, 25071, etc.
        else:
            return {
                'country': 'Unknown',
                'network': 'Unknown',
                'provider': self.primary_provider,
                'confidence': 0.0
            }
        
        # Find matching network
        networks = self.NETWORK_MAPPINGS.get(country, {})
        detected_network = 'Unknown'
        
        for network, prefixes in networks.items():
            if prefix in prefixes:
                detected_network = network
                break
        
        # Determine best provider for this network
        best_provider = self._get_best_provider(country, detected_network)
        
        return {
            'country': country,
            'network': detected_network,
            'provider': best_provider,
            'confidence': 0.9 if detected_network != 'Unknown' else 0.3,
            'prefix': prefix
        }
    
    def _get_best_provider(self, country, network):
        """Get the best SMS provider for a given country and network."""
        # For now, use Beem Africa as primary
        # In production, this would consider:
        # - Provider reliability for specific network
        # - Cost optimization
        # - Current load balancing
        # - Historical success rates
        
        return self.primary_provider
    
    def route_sms(self, phone_number, message, sender_id, user_id):
        """
        Route SMS to the appropriate provider and network.
        
        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message content
            sender_id (str): Sender ID
            user_id (str): User ID for tracking
            
        Returns:
            dict: Routing result
        """
        start_time = time.time()
        
        # Detect network
        network_info = self.detect_network(phone_number)
        
        # Validate compliance
        compliance_result = self._check_compliance(phone_number, message, network_info['country'])
        if not compliance_result['allowed']:
            return {
                'success': False,
                'error': compliance_result['reason'],
                'error_code': 'COMPLIANCE_VIOLATION',
                'network_info': network_info
            }
        
        # Route to appropriate provider
        routing_result = self._route_to_provider(
            phone_number, message, sender_id, user_id, network_info
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': routing_result['success'],
            'message_id': routing_result.get('message_id'),
            'provider': network_info['provider'],
            'network_info': network_info,
            'routing_time_ms': response_time,
            'error': routing_result.get('error'),
            'error_code': routing_result.get('error_code')
        }
    
    def _check_compliance(self, phone_number, message, country):
        """
        Check SMS compliance for different countries.
        
        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message content
            country (str): Country code
            
        Returns:
            dict: Compliance result
        """
        # Basic compliance checks
        if len(message) > 160:
            return {
                'allowed': False,
                'reason': 'Message too long (max 160 characters)'
            }
        
        # Country-specific compliance
        if country == 'Tanzania':
            # Tanzania specific rules
            if 'spam' in message.lower() or 'promotion' in message.lower():
                return {
                    'allowed': False,
                    'reason': 'Message contains prohibited content for Tanzania'
                }
        
        elif country == 'Kenya':
            # Kenya specific rules
            if len(message) > 140:  # Kenya has stricter limits
                return {
                    'allowed': False,
                    'reason': 'Message too long for Kenya (max 140 characters)'
                }
        
        # General compliance
        prohibited_words = ['spam', 'scam', 'fraud']
        if any(word in message.lower() for word in prohibited_words):
            return {
                'allowed': False,
                'reason': 'Message contains prohibited content'
            }
        
        return {'allowed': True, 'reason': 'Compliant'}
    
    def _route_to_provider(self, phone_number, message, sender_id, user_id, network_info):
        """
        Route SMS to the selected provider.
        
        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message content
            sender_id (str): Sender ID
            user_id (str): User ID
            network_info (dict): Network information
            
        Returns:
            dict: Provider routing result
        """
        provider = network_info['provider']
        
        try:
            if provider == 'beem_africa':
                return self._route_to_beem(phone_number, message, sender_id, user_id)
            elif provider == 'africas_talking':
                return self._route_to_africas_talking(phone_number, message, sender_id, user_id)
            elif provider == 'twilio':
                return self._route_to_twilio(phone_number, message, sender_id, user_id)
            else:
                return {
                    'success': False,
                    'error': f'Unknown provider: {provider}',
                    'error_code': 'UNKNOWN_PROVIDER'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'PROVIDER_ERROR'
            }
    
    def _route_to_beem(self, phone_number, message, sender_id, user_id):
        """Route SMS through Beem Africa."""
        try:
            from messaging.services.sms_service import SMSService
            
            sms_service = SMSService(self.tenant_id)
            result = sms_service.send_sms(
                to=phone_number,
                message=message,
                sender_id=sender_id,
                recipient_id=f"agg_{user_id}_{int(timezone.now().timestamp())}"
            )
            
            if result.get('success'):
                # Create message record
                message_obj = Message.objects.create(
                    tenant_id=self.tenant_id,
                    to_number=phone_number,
                    text=message,
                    direction='outbound',
                    status='sent',
                    provider='beem_africa',
                    created_by_id=user_id
                )
                
                return {
                    'success': True,
                    'message_id': str(message_obj.id),
                    'provider_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Beem Africa send failed'),
                    'error_code': 'BEEM_SEND_FAILED'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'BEEM_ERROR'
            }
    
    def _route_to_africas_talking(self, phone_number, message, sender_id, user_id):
        """Route SMS through Africa's Talking (placeholder)."""
        # TODO: Implement Africa's Talking integration
        return {
            'success': False,
            'error': 'Africa\'s Talking integration not implemented',
            'error_code': 'PROVIDER_NOT_IMPLEMENTED'
        }
    
    def _route_to_twilio(self, phone_number, message, sender_id, user_id):
        """Route SMS through Twilio (placeholder)."""
        # TODO: Implement Twilio integration
        return {
            'success': False,
            'error': 'Twilio integration not implemented',
            'error_code': 'PROVIDER_NOT_IMPLEMENTED'
        }
    
    def get_delivery_status(self, message_id):
        """
        Get delivery status for a message.
        
        Args:
            message_id (str): Message ID
            
        Returns:
            dict: Delivery status
        """
        try:
            message = Message.objects.get(id=message_id)
            
            # Determine delivery status
            if message.status == 'delivered':
                delivery_status = 'delivered'
            elif message.status == 'failed':
                delivery_status = 'failed'
            elif message.status == 'sent':
                delivery_status = 'sent'
            else:
                delivery_status = 'pending'
            
            return {
                'success': True,
                'message_id': str(message.id),
                'status': message.status,
                'delivery_status': delivery_status,
                'provider': message.provider,
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
                'error_message': getattr(message, 'error_message', None)
            }
        except Message.DoesNotExist:
            return {
                'success': False,
                'error': 'Message not found',
                'error_code': 'MESSAGE_NOT_FOUND'
            }
    
    def get_network_coverage(self):
        """
        Get network coverage information.
        
        Returns:
            dict: Coverage information
        """
        return {
            'countries': list(self.NETWORK_MAPPINGS.keys()),
            'networks': {
                country: list(networks.keys()) 
                for country, networks in self.NETWORK_MAPPINGS.items()
            },
            'providers': list(self.SMS_PROVIDERS.keys()),
            'total_networks': sum(len(networks) for networks in self.NETWORK_MAPPINGS.values())
        }


# API Views for SMS Aggregator
@api_view(['POST'])
@permission_classes([AllowAny])
def register_sms_aggregator_user(request):
    """
    Register a new SMS Aggregator user.
    This creates an API account for SMS aggregation services.
    """
    try:
        # Validate required fields
        required_fields = ['company_name', 'contact_email', 'contact_phone', 'business_type']
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
        from tenants.models import Tenant
        tenant, _ = Tenant.objects.get_or_create(
            name=f"SMS Aggregator - {request.data['company_name']}",
            defaults={
                'description': f"SMS Aggregator account for {request.data['company_name']}",
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
                'business_type': request.data['business_type'],
                'rate_limits': {
                    'per_minute': api_account.rate_limit_per_minute,
                    'per_hour': api_account.rate_limit_per_hour,
                    'per_day': api_account.rate_limit_per_day
                },
                'network_coverage': SMSAggregatorService().get_network_coverage()
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
    """
    Send SMS through the aggregator service.
    This routes SMS to the appropriate African mobile network.
    """
    # For now, use a simple API key validation
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(format_api_response(
            success=False,
            message="Invalid authentication header",
            error_code="INVALID_AUTH_HEADER"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    api_key = auth_header[7:]
    
    # Simple API key validation - in production, use proper validation
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
        # Initialize SMS Aggregator
        aggregator = SMSAggregatorService(str(api_key_obj.api_account.tenant.id))
        
        # Route SMS
        result = aggregator.route_sms(
            phone_number=request.data['to'],
            message=request.data['message'],
            sender_id=request.data.get('sender_id', 'Taarifa-SMS'),
            user_id=str(api_key_obj.api_account.owner.id)
        )
        
        if result['success']:
            # Log usage - simplified for now
            from .models import APIUsageLog
            APIUsageLog.objects.create(
                api_account=api_account,
                api_key=api_key_obj,
                endpoint=request.path,
                method=request.method,
                status_code=200,
                request_ip=request.META.get('REMOTE_ADDR'),
                response_time_ms=result.get('routing_time_ms', 0)
            )
            
            return Response(format_api_response(
                success=True,
                data={
                    'message_id': result['message_id'],
                    'user_id': str(api_key_obj.api_account.owner.id),
                    'to': request.data['to'],
                    'message': request.data['message'],
                    'status': 'sent',
                    'delivery_status': 'pending',
                    'network_info': result['network_info'],
                    'provider': result['provider'],
                    'routing_time_ms': result['routing_time_ms'],
                    'sent_at': timezone.now().isoformat()
                },
                message="SMS routed successfully through aggregator"
            ))
        else:
            return Response(format_api_response(
                success=False,
                message="SMS routing failed",
                error_code=result.get('error_code', 'ROUTING_FAILED'),
                details=result.get('error', 'Unknown error'),
                network_info=result.get('network_info')
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
    """
    Get network coverage information for the SMS aggregator.
    """
    try:
        aggregator = SMSAggregatorService()
        coverage = aggregator.get_network_coverage()
        
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


