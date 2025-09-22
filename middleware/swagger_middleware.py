class SwaggerDocsMiddleware:
    """Middleware to add custom headers for API documentation"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add custom headers for API docs
        if request.path.startswith('/api/'):
            response['X-API-Version'] = '1.0.0'
            response['X-RateLimit-Limit'] = '1000'
            response['X-RateLimit-Window'] = '3600'
        
        return response
    