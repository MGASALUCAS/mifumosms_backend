"""
Rate limiting utilities for API endpoints.
"""
import time
from django.core.cache import cache
from django.conf import settings
from rest_framework.exceptions import Throttled


class RateLimiter:
    """
    Simple token bucket rate limiter using Redis.
    """
    
    def __init__(self, key_prefix, max_requests, window_seconds):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier):
        """
        Check if the request is allowed based on rate limits.
        Returns True if allowed, False if rate limited.
        """
        key = f"{self.key_prefix}:{identifier}"
        
        # Get current count and timestamp
        current_data = cache.get(key, {'count': 0, 'reset_time': time.time()})
        current_time = time.time()
        
        # Reset if window has passed
        if current_time >= current_data['reset_time']:
            current_data = {'count': 0, 'reset_time': current_time + self.window_seconds}
        
        # Check if limit exceeded
        if current_data['count'] >= self.max_requests:
            return False
        
        # Increment count
        current_data['count'] += 1
        cache.set(key, current_data, self.window_seconds)
        
        return True
    
    def get_retry_after(self, identifier):
        """
        Get the number of seconds until the rate limit resets.
        """
        key = f"{self.key_prefix}:{identifier}"
        current_data = cache.get(key, {'count': 0, 'reset_time': time.time()})
        return max(0, int(current_data['reset_time'] - time.time()))


# Predefined rate limiters
USER_RATE_LIMITER = RateLimiter('user_rate', 100, 3600)  # 100 requests per hour per user
TENANT_RATE_LIMITER = RateLimiter('tenant_rate', 1000, 3600)  # 1000 requests per hour per tenant
MESSAGE_RATE_LIMITER = RateLimiter('message_rate', 100, 60)  # 100 messages per minute per tenant


def check_rate_limit(request, limiter, identifier=None):
    """
    Check rate limit and raise exception if exceeded.
    """
    if identifier is None:
        if hasattr(request, 'tenant') and request.tenant:
            identifier = f"tenant:{request.tenant.id}"
        else:
            identifier = f"user:{request.user.id}"
    
    if not limiter.is_allowed(identifier):
        retry_after = limiter.get_retry_after(identifier)
        raise Throttled(detail=f"Rate limit exceeded. Try again in {retry_after} seconds.")
