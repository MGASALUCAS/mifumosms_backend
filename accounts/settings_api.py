"""
Settings API Endpoints for API Key and Webhook Management
For users who have registered normally and want to manage their API keys
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

from api_integration.models import APIAccount, APIKey, Webhook
from api_integration.utils import generate_api_credentials, format_api_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_settings(request):
    """Get user's API settings including keys and webhooks"""
    try:
        # Get or create API account for the user
        try:
            api_account = APIAccount.objects.get(owner=request.user)
        except APIAccount.DoesNotExist:
            # Create new API account
            api_account = APIAccount.objects.create(
                owner=request.user,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or "My API Account",
                description='Personal API account',
                tenant=request.user.get_tenant() if hasattr(request.user, 'get_tenant') else None,
            )
            # Generate account_id if not set
            if not api_account.account_id:
                api_account.generate_account_id()
                api_account.save()
        
        # Get API keys
        api_keys = APIKey.objects.filter(api_account=api_account).order_by('-created_at')
        
        # Get webhooks
        webhooks = Webhook.objects.filter(api_account=api_account).order_by('-created_at')
        
        # Format API keys data
        keys_data = []
        for key in api_keys:
            keys_data.append({
                'id': str(key.id),
                'key_name': key.key_name,
                'api_key': key.api_key,
                'secret_key': key.secret_key,
                'permissions': key.permissions,
                'status': key.status,
                'total_uses': key.total_uses,
                'last_used': key.last_used.isoformat() if key.last_used else None,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
            })
        
        # Format webhooks data
        webhooks_data = []
        for webhook in webhooks:
            webhooks_data.append({
                'id': str(webhook.id),
                'url': webhook.url,
                'events': webhook.events,
                'is_active': webhook.is_active,
                'created_at': webhook.created_at.isoformat(),
                'last_triggered': webhook.last_triggered.isoformat() if webhook.last_triggered else None,
            })
        
        return Response(format_api_response(
            success=True,
            message="API settings retrieved successfully",
            data={
                'api_account': {
                    'id': str(api_account.id),
                    'name': api_account.name,
                    'description': api_account.description,
                    'created_at': api_account.created_at.isoformat(),
                },
                'api_keys': keys_data,
                'webhooks': webhooks_data,
            }
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to retrieve API settings",
            error_code="SETTINGS_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_api_key(request):
    """Create a new API key"""
    try:
        key_name = request.data.get('key_name', '').strip()
        permissions = request.data.get('permissions', ['read', 'write'])
        expires_at = request.data.get('expires_at')
        
        if not key_name:
            return Response(format_api_response(
                success=False,
                message="Key name is required",
                error_code="MISSING_KEY_NAME"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create API account
        try:
            api_account = APIAccount.objects.get(owner=request.user)
        except APIAccount.DoesNotExist:
            # Create new API account
            api_account = APIAccount.objects.create(
                owner=request.user,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or "My API Account",
                description='Personal API account',
                tenant=request.user.get_tenant() if hasattr(request.user, 'get_tenant') else None,
            )
            # Generate account_id if not set
            if not api_account.account_id:
                api_account.generate_account_id()
                api_account.save()
        
        # Create API key
        api_key = APIKey.objects.create(
            api_account=api_account,
            key_name=key_name,
            permissions=permissions,
            expires_at=expires_at
        )
        
        # Generate credentials
        api_key.api_key, api_key.secret_key = generate_api_credentials()
        api_key.save()
        
        return Response(format_api_response(
            success=True,
            message="API key created successfully",
            data={
                'id': str(api_key.id),
                'key_name': api_key.key_name,
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
                'permissions': api_key.permissions,
                'created_at': api_key.created_at.isoformat(),
                'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
            }
        ), status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to create API key",
            error_code="CREATE_KEY_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_api_key(request, key_id):
    """Revoke an API key"""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
        api_key.revoke()
        
        return Response(format_api_response(
            success=True,
            message="API key revoked successfully",
            data={
                'id': str(api_key.id),
                'status': api_key.status,
                'is_active': api_key.is_active
            }
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to revoke API key",
            error_code="REVOKE_KEY_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_api_key(request, key_id):
    """Regenerate API key credentials"""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
        api_key.api_key, api_key.secret_key = generate_api_credentials()
        api_key.save()
        
        return Response(format_api_response(
            success=True,
            message="API key regenerated successfully",
            data={
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
            }
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to regenerate API key",
            error_code="REGENERATE_KEY_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_webhook(request):
    """Create a new webhook"""
    try:
        url = request.data.get('url', '').strip()
        events = request.data.get('events', [])
        
        if not url:
            return Response(format_api_response(
                success=False,
                message="Webhook URL is required",
                error_code="MISSING_WEBHOOK_URL"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        if not events:
            return Response(format_api_response(
                success=False,
                message="At least one event must be selected",
                error_code="MISSING_WEBHOOK_EVENTS"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create API account
        try:
            api_account = APIAccount.objects.get(owner=request.user)
        except APIAccount.DoesNotExist:
            # Create new API account
            api_account = APIAccount.objects.create(
                owner=request.user,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or "My API Account",
                description='Personal API account',
                tenant=request.user.get_tenant() if hasattr(request.user, 'get_tenant') else None,
            )
            # Generate account_id if not set
            if not api_account.account_id:
                api_account.generate_account_id()
                api_account.save()
        
        # Create webhook
        webhook = Webhook.objects.create(
            api_account=api_account,
            url=url,
            events=events,
            is_active=True
        )
        
        return Response(format_api_response(
            success=True,
            message="Webhook created successfully",
            data={
                'id': str(webhook.id),
                'url': webhook.url,
                'events': webhook.events,
                'is_active': webhook.is_active,
                'created_at': webhook.created_at.isoformat(),
            }
        ), status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to create webhook",
            error_code="CREATE_WEBHOOK_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_webhook(request, webhook_id):
    """Toggle webhook active status"""
    try:
        webhook = get_object_or_404(Webhook, id=webhook_id, api_account__owner=request.user)
        webhook.is_active = not webhook.is_active
        webhook.save()
        
        return Response(format_api_response(
            success=True,
            message=f"Webhook {'activated' if webhook.is_active else 'deactivated'} successfully",
            data={
                'is_active': webhook.is_active
            }
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to toggle webhook",
            error_code="TOGGLE_WEBHOOK_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_webhook(request, webhook_id):
    """Delete a webhook"""
    try:
        webhook = get_object_or_404(Webhook, id=webhook_id, api_account__owner=request.user)
        webhook.delete()
        
        return Response(format_api_response(
            success=True,
            message="Webhook deleted successfully"
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to delete webhook",
            error_code="DELETE_WEBHOOK_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_usage(request):
    """Get API usage statistics for the user"""
    try:
        api_account = get_object_or_404(APIAccount, owner=request.user)
        
        # Get usage statistics
        total_api_keys = APIKey.objects.filter(api_account=api_account).count()
        active_api_keys = APIKey.objects.filter(api_account=api_account, is_active=True).count()
        total_webhooks = Webhook.objects.filter(api_account=api_account).count()
        active_webhooks = Webhook.objects.filter(api_account=api_account, is_active=True).count()
        
        # Get total API calls (sum of all key uses)
        total_api_calls = sum(
            APIKey.objects.filter(api_account=api_account).values_list('total_uses', flat=True)
        )
        
        return Response(format_api_response(
            success=True,
            message="API usage statistics retrieved successfully",
            data={
                'api_keys': {
                    'total': total_api_keys,
                    'active': active_api_keys,
                },
                'webhooks': {
                    'total': total_webhooks,
                    'active': active_webhooks,
                },
                'api_calls': {
                    'total': total_api_calls,
                },
                'account_created': api_account.created_at.isoformat(),
            }
        ), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Failed to retrieve usage statistics",
            error_code="USAGE_STATS_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
