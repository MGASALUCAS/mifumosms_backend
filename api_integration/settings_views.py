"""
Settings Views for API Key and Webhook Management
Similar to the image provided - clean settings interface
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import APIAccount, APIKey, Webhook
from .utils import generate_api_credentials


@login_required
def api_settings(request):
    """Main API settings page - similar to the image"""
    
    # Get or create API account for the user
    api_account, created = APIAccount.objects.get_or_create(
        owner=request.user,
        defaults={
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or "My API Account",
            'description': 'Personal API account',
            'tenant': request.user.get_tenant() if hasattr(request.user, 'get_tenant') else None,
        }
    )
    
    # Get API keys
    api_keys = APIKey.objects.filter(api_account=api_account).order_by('-created_at')
    
    # Get webhooks
    webhooks = Webhook.objects.filter(api_account=api_account).order_by('-created_at')
    
    context = {
        'api_account': api_account,
        'api_keys': api_keys,
        'webhooks': webhooks,
        'user': request.user,
    }
    
    return render(request, 'api_integration/settings.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_api_key(request):
    """Create a new API key"""
    try:
        data = json.loads(request.body)
        key_name = data.get('key_name', '').strip()
        permissions = data.get('permissions', ['read', 'write'])
        expires_at = data.get('expires_at')
        
        if not key_name:
            return JsonResponse({
                'success': False,
                'error': 'Key name is required'
            }, status=400)
        
        # Get API account
        api_account = get_object_or_404(APIAccount, owner=request.user)
        
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
        
        return JsonResponse({
            'success': True,
            'message': 'API key created successfully',
            'data': {
                'id': str(api_key.id),
                'key_name': api_key.key_name,
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
                'permissions': api_key.permissions,
                'created_at': api_key.created_at.isoformat(),
                'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
                'last_used': api_key.last_used.isoformat() if api_key.last_used else None,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def revoke_api_key(request, key_id):
    """Revoke an API key"""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
        api_key.revoke()
        
        return JsonResponse({
            'success': True,
            'message': 'API key revoked successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def regenerate_api_key(request, key_id):
    """Regenerate API key credentials"""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
        api_key.api_key, api_key.secret_key = generate_api_credentials()
        api_key.save()
        
        return JsonResponse({
            'success': True,
            'message': 'API key regenerated successfully',
            'data': {
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_webhook(request):
    """Create a new webhook"""
    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
        events = data.get('events', [])
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'Webhook URL is required'
            }, status=400)
        
        if not events:
            return JsonResponse({
                'success': False,
                'error': 'At least one event must be selected'
            }, status=400)
        
        # Get API account
        api_account = get_object_or_404(APIAccount, owner=request.user)
        
        # Create webhook
        webhook = Webhook.objects.create(
            api_account=api_account,
            url=url,
            events=events,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Webhook created successfully',
            'data': {
                'id': str(webhook.id),
                'url': webhook.url,
                'events': webhook.events,
                'is_active': webhook.is_active,
                'created_at': webhook.created_at.isoformat(),
                'last_triggered': webhook.last_triggered.isoformat() if webhook.last_triggered else None,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def toggle_webhook(request, webhook_id):
    """Toggle webhook active status"""
    try:
        webhook = get_object_or_404(Webhook, id=webhook_id, api_account__owner=request.user)
        webhook.is_active = not webhook.is_active
        webhook.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Webhook {"activated" if webhook.is_active else "deactivated"} successfully',
            'data': {
                'is_active': webhook.is_active
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_webhook(request, webhook_id):
    """Delete a webhook"""
    try:
        webhook = get_object_or_404(Webhook, id=webhook_id, api_account__owner=request.user)
        webhook.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Webhook deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

