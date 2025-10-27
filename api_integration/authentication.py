"""
API Authentication classes for external integrations.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import APIKey, APIAccount
from .utils import validate_api_credentials, get_client_ip, log_api_usage


class APIKeyAuthentication(BaseAuthentication):
    """
    API Key authentication for external integrations.
    
    Expected header format:
    Authorization: Bearer mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    
    def authenticate(self, request):
        """
        Authenticate using API key from Authorization header.
        
        Args:
            request: Django request object
        
        Returns:
            tuple: (api_key_obj, None) if successful
            None: if authentication failed
        """
        # Get API key from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        if not api_key:
            return None
        
        # Validate API key
        is_valid, api_key_obj, error_message = validate_api_credentials(api_key)
        
        if not is_valid:
            raise AuthenticationFailed(error_message or "Invalid API key")
        
        # Check if account is active
        if not api_key_obj.api_account.is_active:
            raise AuthenticationFailed("API account is inactive")
        
        # Check rate limiting
        if api_key_obj.api_account.is_rate_limited('minute'):
            raise AuthenticationFailed("Rate limit exceeded (per minute)")
        
        if api_key_obj.api_account.is_rate_limited('hour'):
            raise AuthenticationFailed("Rate limit exceeded (per hour)")
        
        if api_key_obj.api_account.is_rate_limited('day'):
            raise AuthenticationFailed("Rate limit exceeded (per day)")
        
        # Get client IP for logging
        client_ip = get_client_ip(request)
        
        # Log the authentication (successful)
        log_api_usage(
            api_account=api_key_obj.api_account,
            api_key=api_key_obj,
            integration=None,  # Will be set by the view if available
            endpoint=request.path,
            method=request.method,
            status_code=200,  # Will be updated by the view
            ip_address=client_ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_size=len(request.body) if hasattr(request, 'body') else 0,
            response_size=0,  # Will be updated by the view
            response_time_ms=0,  # Will be updated by the view
        )
        
        return (api_key_obj, None)
    
    def authenticate_header(self, request):
        """
        Return the authentication header value.
        """
        return 'Bearer'


class APIKeySecretAuthentication(BaseAuthentication):
    """
    API Key + Secret authentication for enhanced security.
    
    Expected header format:
    Authorization: Bearer mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    X-API-Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    
    def authenticate(self, request):
        """
        Authenticate using API key and secret from headers.
        
        Args:
            request: Django request object
        
        Returns:
            tuple: (api_key_obj, None) if successful
            None: if authentication failed
        """
        # Get API key from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get secret from X-API-Secret header
        secret_key = request.META.get('HTTP_X_API_SECRET', '')
        
        if not api_key or not secret_key:
            return None
        
        # Validate API key and secret
        is_valid, api_key_obj, error_message = validate_api_credentials(api_key, secret_key)
        
        if not is_valid:
            raise AuthenticationFailed(error_message or "Invalid API credentials")
        
        # Check if account is active
        if not api_key_obj.api_account.is_active:
            raise AuthenticationFailed("API account is inactive")
        
        # Check rate limiting
        if api_key_obj.api_account.is_rate_limited('minute'):
            raise AuthenticationFailed("Rate limit exceeded (per minute)")
        
        if api_key_obj.api_account.is_rate_limited('hour'):
            raise AuthenticationFailed("Rate limit exceeded (per hour)")
        
        if api_key_obj.api_account.is_rate_limited('day'):
            raise AuthenticationFailed("Rate limit exceeded (per day)")
        
        # Get client IP for logging
        client_ip = get_client_ip(request)
        
        # Log the authentication (successful)
        log_api_usage(
            api_account=api_key_obj.api_account,
            api_key=api_key_obj,
            integration=None,  # Will be set by the view if available
            endpoint=request.path,
            method=request.method,
            status_code=200,  # Will be updated by the view
            ip_address=client_ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_size=len(request.body) if hasattr(request, 'body') else 0,
            response_size=0,  # Will be updated by the view
            response_time_ms=0,  # Will be updated by the view
        )
        
        return (api_key_obj, None)
    
    def authenticate_header(self, request):
        """
        Return the authentication header value.
        """
        return 'Bearer'


class AccountIDAuthentication(BaseAuthentication):
    """
    Account ID authentication for simple integrations.
    
    Expected header format:
    X-Account-ID: ACCOUNT_ID_HERE
    X-API-Key: API_KEY_HERE
    """
    
    def authenticate(self, request):
        """
        Authenticate using Account ID and API Key from headers.
        
        Args:
            request: Django request object
        
        Returns:
            tuple: (api_account, None) if successful
            None: if authentication failed
        """
        # Get Account ID and API Key from headers
        account_id = request.META.get('HTTP_X_ACCOUNT_ID', '')
        api_key = request.META.get('HTTP_X_API_KEY', '')
        
        if not account_id or not api_key:
            return None
        
        try:
            # Get API account
            api_account = APIAccount.objects.get(
                account_id=account_id,
                is_active=True
            )
            
            # Get API key
            api_key_obj = APIKey.objects.get(
                api_key=api_key,
                api_account=api_account,
                is_active=True
            )
            
            # Check if key is valid
            if not api_key_obj.is_valid():
                raise AuthenticationFailed("API key is expired or revoked")
            
            # Check rate limiting
            if api_account.is_rate_limited('minute'):
                raise AuthenticationFailed("Rate limit exceeded (per minute)")
            
            if api_account.is_rate_limited('hour'):
                raise AuthenticationFailed("Rate limit exceeded (per hour)")
            
            if api_account.is_rate_limited('day'):
                raise AuthenticationFailed("Rate limit exceeded (per day)")
            
            # Get client IP for logging
            client_ip = get_client_ip(request)
            
            # Log the authentication (successful)
            log_api_usage(
                api_account=api_account,
                api_key=api_key_obj,
                integration=None,  # Will be set by the view if available
                endpoint=request.path,
                method=request.method,
                status_code=200,  # Will be updated by the view
                ip_address=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_size=len(request.body) if hasattr(request, 'body') else 0,
                response_size=0,  # Will be updated by the view
                response_time_ms=0,  # Will be updated by the view
            )
            
            return (api_account, None)
            
        except APIAccount.DoesNotExist:
            raise AuthenticationFailed("Invalid account ID")
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")
    
    def authenticate_header(self, request):
        """
        Return the authentication header value.
        """
        return 'X-Account-ID'






