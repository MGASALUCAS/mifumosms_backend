"""
Simple SMS Test API - Bypasses DRF authentication
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def test_sms_send(request):
    """Simple SMS send test that bypasses DRF authentication"""
    try:
        # Get request data
        data = json.loads(request.body)
        
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'message': 'Authentication required',
                'error_code': 'AUTHENTICATION_REQUIRED'
            }, status=401)
        
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Simple API key validation (just check if it starts with 'mif_')
        if not api_key.startswith('mif_'):
            return JsonResponse({
                'success': False,
                'message': 'Invalid API key format',
                'error_code': 'INVALID_API_KEY'
            }, status=401)
        
        # Extract SMS data
        message = data.get('message', '')
        recipients = data.get('recipients', [])
        sender_id = data.get('sender_id', 'Taarifa-SMS')
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': 'Message is required',
                'error_code': 'MISSING_MESSAGE'
            }, status=400)
        
        if not recipients:
            return JsonResponse({
                'success': False,
                'message': 'Recipients are required',
                'error_code': 'MISSING_RECIPIENTS'
            }, status=400)
        
        # Simulate SMS sending
        message_id = f"msg_{hash(api_key + message + str(recipients)) % 1000000}"
        
        return JsonResponse({
            'success': True,
            'message': 'SMS sent successfully',
            'data': {
                'message_id': message_id,
                'recipients': recipients,
                'sender_id': sender_id,
                'status': 'sent',
                'cost': 10.0,
                'currency': 'TZS'
            },
            'error_code': None,
            'details': None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def test_sms_status(request, message_id):
    """Simple SMS status test"""
    return JsonResponse({
        'success': True,
        'message': 'Message status retrieved successfully',
        'data': {
            'message_id': message_id,
            'status': 'delivered',
            'delivery_time': '2025-10-25T20:30:00Z',
            'recipients': [
                {
                    'phone': '+255757347863',
                    'status': 'delivered',
                    'delivery_time': '2025-10-25T20:30:00Z'
                }
            ]
        }
    })

@csrf_exempt
@require_http_methods(["GET"])
def test_sms_balance(request):
    """Simple SMS balance test"""
    return JsonResponse({
        'success': True,
        'message': 'Balance retrieved successfully',
        'data': {
            'balance': 5000.0,
            'currency': 'TZS',
            'last_updated': '2025-10-25T20:30:00Z'
        }
    })
