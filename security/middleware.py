from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Unified security middleware"""
    
    # Patterns for endpoints that should be exempt from rate limiting
    EXEMPT_PATTERNS = [
        r'^/docs/?$',
        r'^/swagger/?$',
        r'^/redoc/?$',
        r'^/api/schema/?$',
        r'^/api-docs/?$',
        r'^/openapi\.json$',
        r'^/swagger\.json$',
        r'^/admin/',  # Django admin
        r'^/static/',  # Static files
        r'^/media/',   # Media files
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for better performance
        self.compiled_patterns = [re.compile(pattern) for pattern in self.EXEMPT_PATTERNS]

    def __call__(self, request):
        # Check if this path should be exempt from rate limiting
        if not self._is_exempt_path(request.path):
            # Rate limiting only for non-exempt paths
            if not self._check_rate_limit(request):
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
        
        # Security headers (apply to all responses)
        response = self.get_response(request)
        self._add_security_headers(response, request)
        return response

    def _is_exempt_path(self, path):
        """Check if the path should be exempt from rate limiting"""
        return any(pattern.match(path) for pattern in self.compiled_patterns)

    def _check_rate_limit(self, request):
        """Simple rate limiting"""
        client_ip = self._get_client_ip(request)
        key = f"rate_limit:{client_ip}"
        
        # Get current count
        current = cache.get(key, 0)
        if current >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Increment counter
        cache.set(key, current + 1, 60)
        return True

    def _get_client_ip(self, request):
        """Get client IP address"""
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def _add_security_headers(self, response, request):
        """Add security headers with special handling for docs"""
        # Relaxed CSP for documentation endpoints
        if self._is_exempt_path(request.path):
            csp = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
        else:
            csp = "default-src 'self'"
        
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': csp,
        }
        
        # Don't set X-Frame-Options for docs (Swagger UI might need iframes)
        if not self._is_exempt_path(request.path):
            headers['X-Frame-Options'] = 'DENY'
        
        for header, value in headers.items():
            response[header] = value
