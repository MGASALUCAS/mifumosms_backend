"""
Dashboard views for API key management.
Similar to African's Talking and Beem Africa patterns.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
import json
import secrets
import string

from .models import APIAccount, APIKey, APIIntegration, APIUsageLog
from .utils import generate_api_credentials, validate_webhook_url


@login_required
def api_dashboard(request):
    """Main API dashboard showing keys and webhooks."""
    # Get or create API account for user
    api_account, created = APIAccount.objects.get_or_create(
        owner=request.user,
        defaults={
            'name': f"{request.user.get_full_name() or request.user.email}'s API Account",
            'description': 'Default API account',
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000,
            'rate_limit_per_day': 10000,
        }
    )
    
    # Get API keys
    api_keys = APIKey.objects.filter(api_account=api_account).order_by('-created_at')
    
    # Get webhooks (integrations)
    webhooks = APIIntegration.objects.filter(api_account=api_account).order_by('-created_at')
    
    # Get recent activity
    recent_activity = APIUsageLog.objects.filter(
        api_account=api_account
    ).order_by('-timestamp')[:10]
    
    # Calculate stats
    total_api_calls = api_account.total_api_calls
    active_keys = api_keys.filter(is_active=True).count()
    active_webhooks = webhooks.filter(is_active=True).count()
    
    # Calculate success rate
    total_requests = recent_activity.count()
    successful_requests = recent_activity.filter(status_code__lt=400).count()
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
    
    context = {
        'api_account': api_account,
        'api_keys': api_keys,
        'webhooks': webhooks,
        'recent_activity': recent_activity,
        'stats': {
            'total_api_calls': total_api_calls,
            'active_keys': active_keys,
            'active_webhooks': active_webhooks,
            'success_rate': round(success_rate, 1),
        }
    }
    
    return render(request, 'api_integration/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def create_api_key(request):
    """Create a new API key."""
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
def revoke_api_key(request, key_id):
    """Revoke an API key."""
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
def regenerate_api_key(request, key_id):
    """Regenerate API key credentials."""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, api_account__owner=request.user)
        
        # Generate new credentials
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
def create_webhook(request):
    """Create a new webhook."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        webhook_url = data.get('webhook_url', '').strip()
        events = data.get('events', [])
        platform = data.get('platform', 'custom')
        
        if not name or not webhook_url:
            return JsonResponse({
                'success': False,
                'error': 'Name and webhook URL are required'
            }, status=400)
        
        # Validate webhook URL
        is_valid, error_message = validate_webhook_url(webhook_url)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)
        
        # Get API account
        api_account = get_object_or_404(APIAccount, owner=request.user)
        
        # Create webhook
        webhook = APIIntegration.objects.create(
            api_account=api_account,
            name=name,
            platform=platform,
            webhook_url=webhook_url,
            config={'events': events},
            status='active'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Webhook created successfully',
            'data': {
                'id': str(webhook.id),
                'name': webhook.name,
                'webhook_url': webhook.webhook_url,
                'events': events,
                'platform': webhook.platform,
                'status': webhook.status,
                'created_at': webhook.created_at.isoformat(),
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
def toggle_webhook(request, webhook_id):
    """Toggle webhook active status."""
    try:
        webhook = get_object_or_404(APIIntegration, id=webhook_id, api_account__owner=request.user)
        webhook.is_active = not webhook.is_active
        webhook.status = 'active' if webhook.is_active else 'inactive'
        webhook.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Webhook {"activated" if webhook.is_active else "deactivated"} successfully',
            'data': {
                'is_active': webhook.is_active,
                'status': webhook.status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_webhook(request, webhook_id):
    """Delete a webhook."""
    try:
        webhook = get_object_or_404(APIIntegration, id=webhook_id, api_account__owner=request.user)
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


@login_required
def api_documentation(request):
    """API documentation page."""
    return render(request, 'api_integration/documentation.html')


@login_required
def api_usage_logs(request):
    """API usage logs page."""
    api_account = get_object_or_404(APIAccount, owner=request.user)
    
    # Get logs with pagination
    logs = APIUsageLog.objects.filter(api_account=api_account).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'api_account': api_account,
        'page_obj': page_obj,
        'logs': page_obj,
    }
    
    return render(request, 'api_integration/usage_logs.html', context)


@login_required
def api_settings(request):
    """API settings page."""
    api_account = get_object_or_404(APIAccount, owner=request.user)
    
    if request.method == 'POST':
        # Update settings
        api_account.name = request.POST.get('name', api_account.name)
        api_account.description = request.POST.get('description', api_account.description)
        api_account.rate_limit_per_minute = int(request.POST.get('rate_limit_per_minute', api_account.rate_limit_per_minute))
        api_account.rate_limit_per_hour = int(request.POST.get('rate_limit_per_hour', api_account.rate_limit_per_hour))
        api_account.rate_limit_per_day = int(request.POST.get('rate_limit_per_day', api_account.rate_limit_per_day))
        api_account.save()
        
        messages.success(request, 'Settings updated successfully')
        return redirect('api_integration:api_settings')
    
    context = {
        'api_account': api_account,
    }
    
    return render(request, 'api_integration/settings.html', context)

