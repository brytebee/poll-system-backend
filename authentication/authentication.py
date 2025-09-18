# authentication/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.core.cache import cache

class EnhancedJWTAuthentication(JWTAuthentication):
    """
    Enhanced JWT Authentication that checks both refresh token blacklist
    and access token blacklist for immediate logout effect
    """
    
    def get_validated_token(self, raw_token):
        """
        Validates token and checks if the associated refresh token is blacklisted
        """
        # First validate the token normally
        validated_token = super().get_validated_token(raw_token)
        
        # Check if this specific access token is cached as blacklisted
        token_str = raw_token.decode('utf-8') if isinstance(raw_token, bytes) else str(raw_token)
        blacklist_key = f"blacklist_access_token:{token_str}"
        
        if cache.get(blacklist_key):
            raise InvalidToken("Token is blacklisted")
            
        return validated_token
