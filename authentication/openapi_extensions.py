# authentication/openapi_extensions.py
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class EnhancedJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    """OpenAPI extension for EnhancedJWTAuthentication"""
    target_class = 'authentication.authentication.EnhancedJWTAuthentication'
    name = 'EnhancedJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter JWT token with "Bearer " prefix (e.g., "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")'
        }
    