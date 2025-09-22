from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from drf_spectacular.utils import extend_schema

class APIInfoView(APIView):
    """API Information endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="API Information",
        description="Get general API information and status",
        tags=['API Info']
    )
    def get(self, request):
        return Response({
            'name': 'Online Poll System API',
            'version': '1.0.0',
            'description': 'A comprehensive polling system API',
            'status': 'active',
            'documentation_url': request.build_absolute_uri('/api/docs/'),
            'schema_url': request.build_absolute_uri('/api/schema/'),
            'contact': {
                'email': 'support@yourpollsystem.com'
            }
        })

class APIHealthView(APIView):
    """API Health check endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Health Check",
        description="Check API health status",
        tags=['API Info']
    )
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now(),
            'version': '1.0.0'
        })
