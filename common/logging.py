# common/logging.py
from django.conf import settings

def setup_logging():
    """Configure structured logging"""
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {name} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/app.log',
                'formatter': 'detailed',
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/errors.log',
                'formatter': 'detailed',
                'level': 'ERROR',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'polls': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
    
    return LOGGING
