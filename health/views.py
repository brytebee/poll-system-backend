# health/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import extend_schema
import time

class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Health Check",
        description="Check system health status",
        tags=['Health']
    )
    def get(self, request):
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'timestamp': timezone.now(),
            'status': 'healthy'
        }
        
        if any(check.get('status') == 'unhealthy' for check in checks.values() if isinstance(check, dict)):
            checks['status'] = 'unhealthy'
            
        status_code = 200 if checks['status'] == 'healthy' else 503
        return Response(checks, status=status_code)
    
    def _check_database(self):
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            duration = (time.time() - start) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration, 2)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_cache(self):
        try:
            test_key = 'health_check'
            cache.set(test_key, 'ok', 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            
            return {
                'status': 'healthy' if result == 'ok' else 'unhealthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
