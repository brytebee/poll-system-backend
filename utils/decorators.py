# utils/decorators.py
from functools import wraps
from django.core.cache import cache
from common.logging import setup_logging
import time
import logging

logger = logging.getLogger(__name__)

def monitor_performance(threshold_seconds=2.0):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > threshold_seconds:
                logger.warning(f"Slow function: {func.__name__} took {duration:.2f}s")
            
            return result
        return wrapper
    return decorator

def cache_result(timeout=300, key_prefix=''):
    """Simple caching decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

# Quick setup script
def setup_security_and_monitoring():
    """One-time setup function"""
    import os
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Initialize logging
    import logging.config
    logging.config.dictConfig(setup_logging())
    
    print("Security and monitoring setup complete!")
