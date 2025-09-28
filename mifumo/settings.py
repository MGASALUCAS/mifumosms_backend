"""
Django settings for mifumo project.
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='.localhost,.mifumo.local,127.0.0.1,localhost').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',
    'allauth.account',
    'django_celery_beat',
    'django_filters',
    'drf_yasg',
]

LOCAL_APPS = [
    'core',
    'tenants',
    'accounts',
    'messaging',
    'billing',
    'api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.TenantMiddleware',
    'core.middleware.RequestLoggingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mifumo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mifumo.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# WhatsApp Business Cloud API
WA_PHONE_NUMBER_ID = config('WA_PHONE_NUMBER_ID', default='')
WA_TOKEN = config('WA_TOKEN', default='')
WA_VERIFY_TOKEN = config('WA_VERIFY_TOKEN', default='')
WA_API_BASE = config('WA_API_BASE', default='https://graph.facebook.com/v20.0')

# Hugging Face AI
HF_API_URL = config('HF_API_URL', default='')
HF_API_KEY = config('HF_API_KEY', default='')

# Stripe
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# SMS Providers
# Beem Africa SMS
BEEM_API_KEY = config('BEEM_API_KEY', default='')
BEEM_SECRET_KEY = config('BEEM_SECRET_KEY', default='')
BEEM_DEFAULT_SENDER_ID = config('BEEM_DEFAULT_SENDER_ID', default='MIFUMO')
BEEM_API_TIMEOUT = config('BEEM_API_TIMEOUT', default=30, cast=int)
BEEM_API_BASE_URL = config('BEEM_API_BASE_URL', default='https://apisms.beem.africa/v1')
BEEM_SEND_URL = config('BEEM_SEND_URL', default='https://apisms.beem.africa/v1/send')
BEEM_BALANCE_URL = config('BEEM_BALANCE_URL', default='https://apisms.beem.africa/public/v1/vendors/balance')
BEEM_DELIVERY_URL = config('BEEM_DELIVERY_URL', default='https://dlrapi.beem.africa/public/v1/delivery-reports')
BEEM_SENDER_URL = config('BEEM_SENDER_URL', default='https://apisms.beem.africa/public/v1/sender-names')
BEEM_TEMPLATE_URL = config('BEEM_TEMPLATE_URL', default='https://apisms.beem.africa/public/v1/sms-templates')

# Optional: Twilio SMS
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Optional: Telegram
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')

# Base URL
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_FROM_NAME = config('EMAIL_FROM_NAME', default='Mifumo WMS')
EMAIL_FROM_ADDRESS = config('EMAIL_FROM_ADDRESS', default='noreply@mifumo.com')

# File Storage (AWS S3)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
AWS_DEFAULT_ACL = config('AWS_DEFAULT_ACL', default='private')
AWS_S3_FILE_OVERWRITE = config('AWS_S3_FILE_OVERWRITE', default=False, cast=bool)
AWS_S3_VERIFY = config('AWS_S3_VERIFY', default=True, cast=bool)

# Cloudinary (Alternative to S3)
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')

# Monitoring & Logging
SENTRY_DSN = config('SENTRY_DSN', default='')
LOG_LEVEL = config('LOG_LEVEL', default='INFO')

# Security Configuration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)

# Session Configuration
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)

# CSRF Configuration
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool)

# JWT Configuration
JWT_SECRET_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME = config('JWT_ACCESS_TOKEN_LIFETIME', default=3600, cast=int)
JWT_REFRESH_TOKEN_LIFETIME = config('JWT_REFRESH_TOKEN_LIFETIME', default=604800, cast=int)

# Rate Limiting
RATE_LIMIT_MESSAGES_PER_MINUTE = config('RATE_LIMIT_MESSAGES_PER_MINUTE', default=60, cast=int)
RATE_LIMIT_API_CALLS_PER_MINUTE = config('RATE_LIMIT_API_CALLS_PER_MINUTE', default=1000, cast=int)
RATE_LIMIT_SMS_PER_HOUR = config('RATE_LIMIT_SMS_PER_HOUR', default=1000, cast=int)

# Webhook Configuration
WEBHOOK_SECRET_WHATSAPP = config('WEBHOOK_SECRET_WHATSAPP', default='')
WEBHOOK_SECRET_STRIPE = config('WEBHOOK_SECRET_STRIPE', default='')
WEBHOOK_SECRET_SMS = config('WEBHOOK_SECRET_SMS', default='')

# Third-party Integrations
SLACK_BOT_TOKEN = config('SLACK_BOT_TOKEN', default='')
SLACK_WEBHOOK_URL = config('SLACK_WEBHOOK_URL', default='')
TEAMS_WEBHOOK_URL = config('TEAMS_WEBHOOK_URL', default='')

# Business Configuration
COMPANY_NAME = config('COMPANY_NAME', default='Mifumo Labs')
COMPANY_EMAIL = config('COMPANY_EMAIL', default='hello@mifumo.com')
COMPANY_PHONE = config('COMPANY_PHONE', default='+255700000000')
COMPANY_ADDRESS = config('COMPANY_ADDRESS', default='Dar es Salaam, Tanzania')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@mifumo.com')
SUPPORT_PHONE = config('SUPPORT_PHONE', default='+255700000001')

# Feature Flags
ENABLE_AI_FEATURES = config('ENABLE_AI_FEATURES', default=True, cast=bool)
ENABLE_SMS_FEATURES = config('ENABLE_SMS_FEATURES', default=True, cast=bool)
ENABLE_WHATSAPP_FEATURES = config('ENABLE_WHATSAPP_FEATURES', default=True, cast=bool)
ENABLE_BILLING_FEATURES = config('ENABLE_BILLING_FEATURES', default=True, cast=bool)
ENABLE_ANALYTICS = config('ENABLE_ANALYTICS', default=True, cast=bool)
ENABLE_WEBHOOKS = config('ENABLE_WEBHOOKS', default=True, cast=bool)

# API Configuration
API_VERSION = config('API_VERSION', default='v1')
API_RATE_LIMIT = config('API_RATE_LIMIT', default=1000, cast=int)
API_PAGINATION_SIZE = config('API_PAGINATION_SIZE', default=20, cast=int)
API_MAX_PAGE_SIZE = config('API_MAX_PAGE_SIZE', default=100, cast=int)

# Notification Settings
FCM_SERVER_KEY = config('FCM_SERVER_KEY', default='')
FCM_SENDER_ID = config('FCM_SENDER_ID', default='')
SMS_NOTIFICATION_ENABLED = config('SMS_NOTIFICATION_ENABLED', default=True, cast=bool)
SMS_NOTIFICATION_SENDER_ID = config('SMS_NOTIFICATION_SENDER_ID', default='NOTIFY')
EMAIL_NOTIFICATION_ENABLED = config('EMAIL_NOTIFICATION_ENABLED', default=True, cast=bool)
EMAIL_NOTIFICATION_FROM = config('EMAIL_NOTIFICATION_FROM', default='noreply@mifumo.com')

# Backup Configuration
BACKUP_ENABLED = config('BACKUP_ENABLED', default=True, cast=bool)
BACKUP_SCHEDULE = config('BACKUP_SCHEDULE', default='0 2 * * *')
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)
BACKUP_S3_BUCKET = config('BACKUP_S3_BUCKET', default='')

# Caching Configuration
CACHE_TTL = config('CACHE_TTL', default=300, cast=int)
CACHE_MAX_ENTRIES = config('CACHE_MAX_ENTRIES', default=1000, cast=int)
CACHE_CULL_FREQUENCY = config('CACHE_CULL_FREQUENCY', default=3, cast=int)

# Analytics Configuration
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
MIXPANEL_TOKEN = config('MIXPANEL_TOKEN', default='')

# Security Headers
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='DENY')

# Custom Settings
DEFAULT_TIMEZONE = config('DEFAULT_TIMEZONE', default='Africa/Dar_es_Salaam')
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='USD')
DEFAULT_LANGUAGE = config('DEFAULT_LANGUAGE', default='en')

# Message Limits
MAX_MESSAGE_LENGTH = config('MAX_MESSAGE_LENGTH', default=160, cast=int)
MAX_BULK_MESSAGES = config('MAX_BULK_MESSAGES', default=1000, cast=int)
MAX_CONTACTS_PER_TENANT = config('MAX_CONTACTS_PER_TENANT', default=10000, cast=int)

# Cost Settings
SMS_COST_PER_MESSAGE = config('SMS_COST_PER_MESSAGE', default=0.05, cast=float)
WHATSAPP_COST_PER_MESSAGE = config('WHATSAPP_COST_PER_MESSAGE', default=0.01, cast=float)
FREE_MESSAGES_LIMIT = config('FREE_MESSAGES_LIMIT', default=100, cast=int)

# Django Allauth Configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'mifumo': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Sentry (optional)
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN and SENTRY_DSN.strip():
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1,
            send_default_pii=True,
        )
    except Exception as e:
        # Log the error but don't crash the application
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to initialize Sentry: {e}")
        logger.warning("Continuing without Sentry monitoring")
