"""
Test configuration for billing API tests.
"""
import os
import django
from django.conf import settings

# Set up Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

# Test database configuration
TEST_DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Test settings
TEST_SETTINGS = {
    'DEBUG': True,
    'SECRET_KEY': 'test-secret-key-for-testing-only',
    'DATABASES': TEST_DATABASE,
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'rest_framework',
        'rest_framework_simplejwt',
        'django_filters',
        'drf_yasg',
        'accounts',
        'billing',
        'tenants',
        'messaging',
        'core',
    ],
    'AUTH_USER_MODEL': 'accounts.User',
    'REST_FRAMEWORK': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    },
    'SIMPLE_JWT': {
        'ACCESS_TOKEN_LIFETIME': 60 * 60,  # 1 hour
        'REFRESH_TOKEN_LIFETIME': 7 * 24 * 60 * 60,  # 7 days
    },
    'BASE_URL': 'http://localhost:8000',
    'ZENOPAY_API_URL': 'https://api.zenopay.com',
    'ZENOPAY_API_KEY': 'test-api-key',
    'ZENOPAY_WEBHOOK_SECRET': 'test-webhook-secret',
}
