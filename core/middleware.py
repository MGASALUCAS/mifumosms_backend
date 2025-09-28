"""
Core middleware for multi-tenant support and request logging.
"""
import logging
import time
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant, Domain

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to determine tenant from subdomain or domain.
    Sets request.tenant for use throughout the application.
    """
    
    def process_request(self, request):
        """Set the tenant based on the request's host."""
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Skip tenant resolution for certain paths
        skip_paths = ['/admin/', '/swagger/', '/redoc/', '/webhooks/']
        if any(request.path.startswith(path) for path in skip_paths):
            request.tenant = None
            return
        
        # Try to find tenant by domain
        try:
            domain = Domain.objects.select_related('tenant').get(domain=host)
            request.tenant = domain.tenant
        except Domain.DoesNotExist:
            # Try subdomain matching
            subdomain = host.split('.')[0] if '.' in host else None
            if subdomain and subdomain not in ['www', 'api', 'app']:
                try:
                    request.tenant = Tenant.objects.get(subdomain=subdomain)
                except Tenant.DoesNotExist:
                    request.tenant = None
            else:
                request.tenant = None
        
        # If no tenant found and not in allowed skip paths, try to use default tenant for development
        if not request.tenant and not any(request.path.startswith(path) for path in skip_paths):
            if not request.path.startswith('/api/auth/'):
                # For development, try to use the first available tenant
                try:
                    request.tenant = Tenant.objects.filter(is_active=True).first()
                except Tenant.DoesNotExist:
                    # If no tenant exists at all, allow the request to continue
                    # This is useful for initial setup
                    pass


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests with tenant information.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log request details
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': round(duration, 3),
                'user': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'tenant': getattr(request.tenant, 'id', None) if hasattr(request, 'tenant') else None,
                'ip': self.get_client_ip(request),
            }
            
            logger.info(f"Request processed: {log_data}")
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
