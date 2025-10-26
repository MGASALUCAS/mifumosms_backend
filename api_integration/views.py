"""
Views for API integration system.
"""
import time
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.cache import cache

from .models import APIAccount, APIKey, APIIntegration, APIUsageLog
from .serializers import (
    APIAccountSerializer, APIAccountCreateSerializer,
    APIKeySerializer, APIKeyCreateSerializer,
    APIIntegrationSerializer, APIIntegrationCreateSerializer,
    APIUsageLogSerializer, APIAccountStatsSerializer,
    APIKeyStatsSerializer, IntegrationStatsSerializer
)
from .utils import get_rate_limit_info, format_api_response, get_client_ip
from .authentication import APIKeyAuthentication, AccountIDAuthentication


class APIAccountListCreateView(generics.ListCreateAPIView):
    """List and create API accounts."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIAccountCreateSerializer
        return APIAccountSerializer
    
    def get_queryset(self):
        """Return API accounts for the current user."""
        return APIAccount.objects.filter(owner=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create API account for the current user."""
        serializer.save()


class APIAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete API account."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = APIAccountSerializer
    
    def get_queryset(self):
        """Return API accounts for the current user."""
        return APIAccount.objects.filter(owner=self.request.user)


class APIKeyListCreateView(generics.ListCreateAPIView):
    """List and create API keys for an account."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def get_queryset(self):
        """Return API keys for the specified account."""
        account_id = self.kwargs['account_id']
        account = get_object_or_404(APIAccount, id=account_id, owner=self.request.user)
        return APIKey.objects.filter(api_account=account).order_by('-created_at')
    
    def get_serializer_context(self):
        """Add API account to context."""
        context = super().get_serializer_context()
        account_id = self.kwargs['account_id']
        account = get_object_or_404(APIAccount, id=account_id, owner=self.request.user)
        context['api_account'] = account
        return context


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete API key."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeySerializer
    
    def get_queryset(self):
        """Return API keys for the current user's accounts."""
        return APIKey.objects.filter(api_account__owner=self.request.user)


class APIIntegrationListCreateView(generics.ListCreateAPIView):
    """List and create API integrations for an account."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIIntegrationCreateSerializer
        return APIIntegrationSerializer
    
    def get_queryset(self):
        """Return integrations for the specified account."""
        account_id = self.kwargs['account_id']
        account = get_object_or_404(APIAccount, id=account_id, owner=self.request.user)
        return APIIntegration.objects.filter(api_account=account).order_by('-created_at')
    
    def get_serializer_context(self):
        """Add API account to context."""
        context = super().get_serializer_context()
        account_id = self.kwargs['account_id']
        account = get_object_or_404(APIAccount, id=account_id, owner=self.request.user)
        context['api_account'] = account
        return context


class APIIntegrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete API integration."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = APIIntegrationSerializer
    
    def get_queryset(self):
        """Return integrations for the current user's accounts."""
        return APIIntegration.objects.filter(api_account__owner=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_account_stats(request, account_id):
    """Get statistics for an API account."""
    account = get_object_or_404(APIAccount, id=account_id, owner=request.user)
    
    # Get rate limit info
    rate_limit_info = get_rate_limit_info(account)
    
    # Calculate success rate
    total_requests = account.usage_logs.count()
    successful_requests = account.usage_logs.filter(status_code__lt=400).count()
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Get last activity
    last_activity = account.usage_logs.order_by('-timestamp').first()
    last_activity_time = last_activity.timestamp if last_activity else None
    
    stats = {
        'account_id': account.account_id,
        'name': account.name,
        'total_api_calls': account.total_api_calls,
        'active_api_keys': account.api_keys.filter(is_active=True).count(),
        'active_integrations': account.integrations.filter(is_active=True).count(),
        'success_rate': round(success_rate, 2),
        'rate_limit_info': rate_limit_info,
        'last_activity': last_activity_time
    }
    
    return Response(format_api_response(
        success=True,
        data=stats,
        message="API account statistics retrieved successfully"
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_key_stats(request, key_id):
    """Get statistics for an API key."""
    api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
    
    stats = {
        'key_name': api_key.key_name,
        'api_key': api_key.api_key,
        'total_uses': api_key.total_uses,
        'last_used': api_key.last_used,
        'last_used_ip': api_key.last_used_ip,
        'is_active': api_key.is_active
    }
    
    return Response(format_api_response(
        success=True,
        data=stats,
        message="API key statistics retrieved successfully"
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def integration_stats(request, integration_id):
    """Get statistics for an integration."""
    integration = get_object_or_404(APIIntegration, id=integration_id, api_account__owner=request.user)
    
    success_rate = (integration.successful_requests / integration.total_requests * 100) if integration.total_requests > 0 else 0
    
    stats = {
        'name': integration.name,
        'platform': integration.platform,
        'total_requests': integration.total_requests,
        'success_rate': round(success_rate, 2),
        'last_request': integration.last_request,
        'is_active': integration.is_active
    }
    
    return Response(format_api_response(
        success=True,
        data=stats,
        message="Integration statistics retrieved successfully"
    ))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_api_key(request, key_id):
    """Revoke an API key."""
    api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
    
    api_key.revoke()
    
    return Response(format_api_response(
        success=True,
        message="API key revoked successfully"
    ))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_api_key(request, key_id):
    """Regenerate API key credentials."""
    api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
    
    # Generate new credentials
    new_api_key, new_secret_key = api_key.generate_keys()
    api_key.save()
    
    return Response(format_api_response(
        success=True,
        data={
            'api_key': new_api_key,
            'secret_key': new_secret_key
        },
        message="API key regenerated successfully"
    ))


# External API Views (for integrations)
class ExternalAPIViewMixin:
    """Mixin for external API views with authentication and logging."""
    
    authentication_classes = [APIKeyAuthentication, AccountIDAuthentication]
    permission_classes = []  # No Django permissions, using custom auth
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add logging and timing."""
        start_time = time.time()
        
        # Get authentication info
        if hasattr(request, 'auth') and request.auth:
            if hasattr(request.auth, 'api_account'):
                self.api_account = request.auth.api_account
                self.api_key = getattr(request.auth, 'api_key', None)
            else:
                self.api_account = request.auth
                self.api_key = None
        else:
            self.api_account = None
            self.api_key = None
        
        # Process request
        response = super().dispatch(request, *args, **kwargs)
        
        # Log usage
        if self.api_account:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            from .utils import log_api_usage
            log_api_usage(
                api_account=self.api_account,
                api_key=self.api_key,
                integration=None,  # Could be determined from request
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_size=len(request.body) if hasattr(request, 'body') else 0,
                response_size=len(response.content) if hasattr(response, 'content') else 0,
                response_time_ms=response_time_ms,
                error_message="" if response.status_code < 400 else "API Error"
            )
        
        return response


@api_view(['GET'])
def external_api_status(request):
    """External API status endpoint."""
    return Response(format_api_response(
        success=True,
        data={
            'status': 'active',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat()
        },
        message="API is operational"
    ))


@api_view(['GET'])
def external_api_info(request):
    """Get API information for authenticated account."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account info
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Get rate limit info
    rate_limit_info = get_rate_limit_info(account)
    
    info = {
        'account_id': account.account_id,
        'account_name': account.name,
        'rate_limits': rate_limit_info,
        'api_version': '1.0.0',
        'endpoints': {
            'sms': '/api/v1/sms/',
            'contacts': '/api/v1/contacts/',
            'campaigns': '/api/v1/campaigns/',
            'templates': '/api/v1/templates/'
        }
    }
    
    return Response(format_api_response(
        success=True,
        data=info,
        message="API information retrieved successfully"
    ))




