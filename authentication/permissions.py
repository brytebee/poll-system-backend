
# authentication/permissions.py
from rest_framework import permissions
from django.core.cache import cache

class NotBlacklistedPermission(permissions.BasePermission):
    """
    Permission that checks if user's session is still valid (not logged out)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Get the access token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return False
            
        access_token = auth_header.split(' ')[1]
        
        # Quick cache check first
        blacklist_key = f"blacklist_access_token:{access_token}"
        if cache.get(blacklist_key):
            return False
            
        return True
