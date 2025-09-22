import logging
import traceback
from django.conf import settings
from django.core.mail import mail_admins
from django.utils import timezone
from django.core.cache import cache
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

class ErrorMonitoringService:
    """Service for monitoring and alerting on errors"""
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None, user=None):
        """Log error with context information"""
        error_data = {
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'timestamp': timezone.now().isoformat(),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'user': user.username if user and hasattr(user, 'username') else None,
        }
        
        logger.error(json.dumps(error_data, indent=2))
        
        # Store in cache for dashboard (last 100 errors)
        errors_key = 'recent_errors'
        recent_errors = cache.get(errors_key, [])
        recent_errors.insert(0, error_data)
        recent_errors = recent_errors[:100]  # Keep only last 100
        cache.set(errors_key, recent_errors, 86400)  # Store for 24 hours
        
        # Send email for critical errors
        if ErrorMonitoringService._is_critical_error(error):
            ErrorMonitoringService._send_error_alert(error_data)
    
    @staticmethod
    def _is_critical_error(error: Exception) -> bool:
        """Determine if error is critical"""
        critical_errors = [
            'DatabaseError',
            'IntegrityError',
            'ConnectionError',
            'MemoryError',
            'SystemError',
        ]
        return error.__class__.__name__ in critical_errors
    
    @staticmethod
    def _send_error_alert(error_data: Dict[str, Any]):
        """Send error alert to administrators"""
        if not settings.DEBUG:
            subject = f"Critical Error in {settings.PROJECT_NAME}"
            message = f"""
            Critical error occurred:
            
            Type: {error_data['error_type']}
            Message: {error_data['error_message']}
            Time: {error_data['timestamp']}
            User: {error_data.get('user', 'Anonymous')}
            
            Context: {json.dumps(error_data.get('context', {}), indent=2)}
            
            Traceback:
            {error_data['traceback']}
            """
            
            try:
                mail_admins(subject, message)
            except Exception as e:
                logger.error(f"Failed to send error alert: {e}")
    
    @staticmethod
    def get_error_statistics() -> Dict[str, Any]:
        """Get error statistics for monitoring dashboard"""
        errors_key = 'recent_errors'
        recent_errors = cache.get(errors_key, [])
        
        if not recent_errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'errors_by_hour': {},
                'most_recent': None
            }
        
        # Count error types
        error_types = {}
        errors_by_hour = {}
        
        for error in recent_errors:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Group by hour
            hour = error['timestamp'][:13]  # YYYY-MM-DDTHH
            errors_by_hour[hour] = errors_by_hour.get(hour, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'errors_by_hour': errors_by_hour,
            'most_recent': recent_errors[0] if recent_errors else None
        }
    
    @staticmethod
    def clear_error_cache():
        """Clear error cache (for testing or maintenance)"""
        cache.delete('recent_errors')

class PerformanceMonitoringService:
    """Service for monitoring application performance"""
    
    @staticmethod
    def log_slow_query(query: str, duration: float, context: Dict[str, Any] = None):
        """Log slow database queries"""
        if duration > 1.0:  # Log queries taking more than 1 second
            logger.warning(
                f"Slow query detected: {duration:.2f}s - {query[:200]}... "
                f"Context: {json.dumps(context or {}, default=str)}"
            )
    
    @staticmethod
    def log_api_performance(view_name: str, duration: float, status_code: int):
        """Log API endpoint performance"""
        cache_key = f"api_performance:{view_name}"
        performance_data = cache.get(cache_key, {
            'total_requests': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'slowest_request': 0,
            'error_count': 0
        })
        
        performance_data['total_requests'] += 1
        performance_data['total_duration'] += duration
        performance_data['avg_duration'] = performance_data['total_duration'] / performance_data['total_requests']
        
        if duration > performance_data['slowest_request']:
            performance_data['slowest_request'] = duration
        
        if status_code >= 400:
            performance_data['error_count'] += 1
        
        cache.set(cache_key, performance_data, 3600)  # Store for 1 hour
        
        # Log slow endpoints
        if duration > 2.0:  # Threshold for slow endpoint
            logger.warning(
                f"Slow API endpoint: {view_name} took {duration:.2f}s (Status: {status_code})"
            )

class HealthCheckService:
    """Service for application health checks"""
    
    @staticmethod
    def check_database_health() -> Dict[str, Any]:
        """Check database connectivity and performance"""
        from django.db import connection
        import time
        
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': round(duration * 1000, 2),  # ms
                'message': 'Database connection successful'
            }
        except Exception as e:
            ErrorMonitoringService.log_error(e, {'check': 'database_health'})
            return {
                'status': 'unhealthy',
                'response_time': None,
                'message': f'Database connection failed: {str(e)}'
            }
    
    @staticmethod
    def check_cache_health() -> Dict[str, Any]:
        """Check cache connectivity"""
        try:
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            if retrieved_value == test_value:
                return {
                    'status': 'healthy',
                    'message': 'Cache is working properly'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Cache test failed'
                }
        except Exception as e:
            """TODO: Add exception code"""
    def post(self, request, *args, **kwargs):
        # ... existing code ...
        pass