"""
Utility functions for API integration.
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta


def check_rate_limit(api_account, time_window='minute'):
    """
    Check if API account is rate limited.
    
    Args:
        api_account: APIAccount instance
        time_window: 'minute', 'hour', or 'day'
    
    Returns:
        bool: True if rate limited, False otherwise
    """
    if not api_account.is_active:
        return True
    
    # Get rate limit for the time window
    if time_window == 'minute':
        limit = api_account.rate_limit_per_minute
        cache_key = f"rate_limit_minute_{api_account.id}"
        window_seconds = 60
    elif time_window == 'hour':
        limit = api_account.rate_limit_per_hour
        cache_key = f"rate_limit_hour_{api_account.id}"
        window_seconds = 3600
    elif time_window == 'day':
        limit = api_account.rate_limit_per_day
        cache_key = f"rate_limit_day_{api_account.id}"
        window_seconds = 86400
    else:
        return False
    
    # Get current count from cache
    current_count = cache.get(cache_key, 0)
    
    # Check if limit exceeded
    if current_count >= limit:
        return True
    
    # Increment counter
    cache.set(cache_key, current_count + 1, window_seconds)
    return False


def get_rate_limit_info(api_account):
    """
    Get rate limit information for an API account.
    
    Args:
        api_account: APIAccount instance
    
    Returns:
        dict: Rate limit information
    """
    from django.core.cache import cache
    
    minute_count = cache.get(f"rate_limit_minute_{api_account.id}", 0)
    hour_count = cache.get(f"rate_limit_hour_{api_account.id}", 0)
    day_count = cache.get(f"rate_limit_day_{api_account.id}", 0)
    
    return {
        'minute': {
            'used': minute_count,
            'limit': api_account.rate_limit_per_minute,
            'remaining': max(0, api_account.rate_limit_per_minute - minute_count)
        },
        'hour': {
            'used': hour_count,
            'limit': api_account.rate_limit_per_hour,
            'remaining': max(0, api_account.rate_limit_per_hour - hour_count)
        },
        'day': {
            'used': day_count,
            'limit': api_account.rate_limit_per_day,
            'remaining': max(0, api_account.rate_limit_per_day - day_count)
        }
    }


def generate_api_credentials():
    """
    Generate API key and secret key pair.
    
    Returns:
        tuple: (api_key, secret_key)
    """
    import secrets
    
    api_key = f"mif_{secrets.token_urlsafe(32)}"
    secret_key = secrets.token_urlsafe(32)
    
    return api_key, secret_key


def validate_api_credentials(api_key, secret_key=None):
    """
    Validate API credentials.
    
    Args:
        api_key: API key to validate
        secret_key: Optional secret key for additional validation
    
    Returns:
        tuple: (is_valid, api_key_obj, error_message)
    """
    from .models import APIKey
    
    try:
        api_key_obj = APIKey.objects.get(api_key=api_key, is_active=True)
        
        # Check if key is valid
        if not api_key_obj.is_valid():
            return False, None, "API key is expired or revoked"
        
        # Check secret key if provided
        if secret_key and api_key_obj.secret_key != secret_key:
            return False, None, "Invalid secret key"
        
        return True, api_key_obj, None
        
    except APIKey.DoesNotExist:
        return False, None, "Invalid API key"


def log_api_usage(api_account, api_key, integration, endpoint, method, 
                 status_code, ip_address, user_agent, request_size=0, 
                 response_size=0, response_time_ms=0, error_message=""):
    """
    Log API usage for monitoring and analytics.
    
    Args:
        api_account: APIAccount instance
        api_key: APIKey instance (optional)
        integration: APIIntegration instance (optional)
        endpoint: API endpoint called
        method: HTTP method
        status_code: HTTP status code
        ip_address: Client IP address
        user_agent: Client user agent
        request_size: Request size in bytes
        response_size: Response size in bytes
        response_time_ms: Response time in milliseconds
        error_message: Error message if any
    """
    from .models import APIUsageLog
    
    # Create usage log entry
    APIUsageLog.objects.create(
        api_account=api_account,
        api_key=api_key,
        integration=integration,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        ip_address=ip_address,
        user_agent=user_agent,
        request_size=request_size,
        response_size=response_size,
        response_time_ms=response_time_ms,
        error_message=error_message
    )
    
    # Update account usage counters
    api_account.increment_api_call()
    
    # Update key usage if provided
    if api_key:
        api_key.increment_use(ip_address)
    
    # Update integration usage if provided
    if integration:
        integration.increment_request(status_code < 400)


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_api_response(success=True, data=None, message="", error_code=None, **kwargs):
    """
    Format standardized API response.
    
    Args:
        success: Whether the request was successful
        data: Response data
        message: Response message
        error_code: Error code if any
        **kwargs: Additional fields
    
    Returns:
        dict: Formatted response
    """
    response = {
        'success': success,
        'timestamp': timezone.now().isoformat(),
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error_code:
        response['error_code'] = error_code
    
    # Add any additional fields
    response.update(kwargs)
    
    return response


def generate_account_id_string():
    """
    Generate a unique account ID string.
    
    Returns:
        str: Unique account ID string
    """
    import secrets
    import string
    
    # Generate a random string with letters and numbers
    characters = string.ascii_letters + string.digits
    account_id = ''.join(secrets.choice(characters) for _ in range(12))
    
    return f"acc_{account_id}"


def validate_webhook_url(url):
    """
    Validate webhook URL format and accessibility.
    
    Args:
        url: Webhook URL to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    import re
    from urllib.parse import urlparse
    
    # Basic URL format validation
    if not url:
        return False, "URL is required"
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
        
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS URLs are allowed"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

