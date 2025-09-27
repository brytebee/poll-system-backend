# health/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
import time

class HealthCheckResponseSerializer(serializers.Serializer):
    """Health check response serializer"""
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.DictField()
    cache = serializers.DictField()

class HealthCheckView(APIView):
    """System health check endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = HealthCheckResponseSerializer
    
    @extend_schema(
        summary="System health check",
        description="Check the health status of system components (database, cache)",
        tags=['Health'],
        responses={
            200: OpenApiResponse(
                response=HealthCheckResponseSerializer,
                description="System is healthy"
            ),
            503: OpenApiResponse(
                response=HealthCheckResponseSerializer,
                description="System has health issues"
            )
        }
    )
    def get(self, request):
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'timestamp': timezone.now(),
            'status': 'healthy'
        }
        
        # Check if any component is unhealthy
        unhealthy_components = [
            name for name, check in checks.items() 
            if isinstance(check, dict) and check.get('status') == 'unhealthy'
        ]
        
        if unhealthy_components:
            checks['status'] = 'unhealthy'
            checks['unhealthy_components'] = unhealthy_components
            
        status_code = 200 if checks['status'] == 'healthy' else 503
        return Response(checks, status=status_code)
    
    def _check_database(self):
        """Check database connectivity and response time"""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            duration = (time.time() - start) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration, 2),
                'connection': 'active'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed'
            }
    
    def _check_cache(self):
        """Check cache connectivity and functionality"""
        try:
            start = time.time()
            test_key = 'health_check_test'
            test_value = 'ok'
            
            # Test cache set operation
            cache.set(test_key, test_value, 10)
            
            # Test cache get operation
            result = cache.get(test_key)
            
            # Clean up test key
            cache.delete(test_key)
            
            duration = (time.time() - start) * 1000
            
            if result == test_value:
                return {
                    'status': 'healthy',
                    'response_time_ms': round(duration, 2),
                    'operations': 'set/get/delete successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache get operation failed',
                    'expected': test_value,
                    'received': result
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'operations': 'failed'
            }
        