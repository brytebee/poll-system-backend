# poll_system/settings/production.py
from .base import *

# Security settings for production
DEBUG = False

ALLOWED_HOSTS = [
    config('DOMAIN_NAME', default='localhost'),
    f"www.{config('DOMAIN_NAME', default='localhost')}",
    config('SERVER_IP', default='127.0.0.1'),
]

# HTTPS settings
SECURE_SSL_REDIRECT = config('USE_HTTPS', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if config('USE_HTTPS', default=False, cast=bool) else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = config('USE_HTTPS', default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# CSRF protection
CSRF_COOKIE_SECURE = config('USE_HTTPS', default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    f"https://{config('DOMAIN_NAME', default='localhost')}",
    f"https://www.{config('DOMAIN_NAME', default='localhost')}",
]

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")

# Database security
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require' if config('USE_DATABASE_SSL', default=False, cast=bool) else 'disable',
}
