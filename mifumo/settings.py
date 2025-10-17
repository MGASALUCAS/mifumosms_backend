"""
Django settings for mifumo project.
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# =============================================================================
# CORE
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='.localhost,.mifumo.local,127.0.0.1,localhost,104.131.116.55,ileana-unsupposed-nonmortally.ngrok-free.dev,*.ngrok-free.dev'
).split(',')

SITE_ID = 1

# =============================================================================
# APPS
# =============================================================================
DJANGO_APPS = [
    'jazzmin',  # must precede django.contrib.admin
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

# =============================================================================
# MIDDLEWARE
# =============================================================================
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
        'DIRS': [BASE_DIR / 'templates'],
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

# =============================================================================
# DATABASE
# =============================================================================
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
#     )
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mifumosms',
        'USER': 'mifumoSuperSms',
        'PASSWORD': 'Hero123\r',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# =============================================================================
# AUTH / USERS
# =============================================================================
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# I18N / TZ
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC / MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# REST FRAMEWORK / JWT
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('API_PAGINATION_SIZE', default=20, cast=int),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=config('JWT_ACCESS_TOKEN_LIFETIME', default=3600, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=config('JWT_REFRESH_TOKEN_LIFETIME', default=604800, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
}

# =============================================================================
# CORS / CSRF
# =============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080'
).split(',')

CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)
CORS_ALLOW_ALL_ORIGINS = DEBUG  # convenience for dev

# Useful CSRF trusted origins (must include scheme)
CSRF_TRUSTED_ORIGINS = [
    origin for origin in CORS_ALLOWED_ORIGINS
    if origin.startswith('http://') or origin.startswith('https://')
]

# Session / CSRF cookies
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool)

# =============================================================================
# CELERY
# =============================================================================
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# INTEGRATIONS / KEYS
# =============================================================================
# WhatsApp
WA_PHONE_NUMBER_ID = config('WA_PHONE_NUMBER_ID', default='')
WA_TOKEN = config('WA_TOKEN', default='')
WA_VERIFY_TOKEN = config('WA_VERIFY_TOKEN', default='')
WA_API_BASE = config('WA_API_BASE', default='https://graph.facebook.com/v20.0')

# Hugging Face
HF_API_URL = config('HF_API_URL', default='')
HF_API_KEY = config('HF_API_KEY', default='')

# Stripe
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# ZenoPay Mobile Money
ZENOPAY_API_KEY = config('ZENOPAY_API_KEY', default='')
ZENOPAY_API_TIMEOUT = config('ZENOPAY_API_TIMEOUT', default=30, cast=int)
ZENOPAY_WEBHOOK_SECRET = config('ZENOPAY_WEBHOOK_SECRET', default='')

# SMS: Beem
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

# Twilio (optional)
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Telegram (optional)
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')

# Base URL (used in webhooks, etc.)
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_FROM_NAME = config('EMAIL_FROM_NAME', default='Mifumo WMS')
EMAIL_FROM_ADDRESS = config('EMAIL_FROM_ADDRESS', default='noreply@mifumo.com')

# Storage (S3)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
AWS_DEFAULT_ACL = config('AWS_DEFAULT_ACL', default='private')
AWS_S3_FILE_OVERWRITE = config('AWS_S3_FILE_OVERWRITE', default=False, cast=bool)
AWS_S3_VERIFY = config('AWS_S3_VERIFY', default=True, cast=bool)

# Cloudinary (optional)
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')

# Webhooks
WEBHOOK_SECRET_WHATSAPP = config('WEBHOOK_SECRET_WHATSAPP', default='')
WEBHOOK_SECRET_STRIPE = config('WEBHOOK_SECRET_STRIPE', default='')
WEBHOOK_SECRET_SMS = config('WEBHOOK_SECRET_SMS', default='')

# Team comms
SLACK_BOT_TOKEN = config('SLACK_BOT_TOKEN', default='')
SLACK_WEBHOOK_URL = config('SLACK_WEBHOOK_URL', default='')
TEAMS_WEBHOOK_URL = config('TEAMS_WEBHOOK_URL', default='')

# Business info
COMPANY_NAME = config('COMPANY_NAME', default='Mifumo Labs')
COMPANY_EMAIL = config('COMPANY_EMAIL', default='hello@mifumo.com')
COMPANY_PHONE = config('COMPANY_PHONE', default='+255700000000')
COMPANY_ADDRESS = config('COMPANY_ADDRESS', default='Dar es Salaam, Tanzania')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@mifumo.com')
SUPPORT_PHONE = config('SUPPORT_PHONE', default='+255700000001')

# Feature flags
ENABLE_AI_FEATURES = config('ENABLE_AI_FEATURES', default=True, cast=bool)
ENABLE_SMS_FEATURES = config('ENABLE_SMS_FEATURES', default=True, cast=bool)
ENABLE_WHATSAPP_FEATURES = config('ENABLE_WHATSAPP_FEATURES', default=True, cast=bool)
ENABLE_BILLING_FEATURES = config('ENABLE_BILLING_FEATURES', default=True, cast=bool)
ENABLE_ANALYTICS = config('ENABLE_ANALYTICS', default=True, cast=bool)
ENABLE_WEBHOOKS = config('ENABLE_WEBHOOKS', default=True, cast=bool)

# API housekeeping
API_VERSION = config('API_VERSION', default='v1')
API_RATE_LIMIT = config('API_RATE_LIMIT', default=1000, cast=int)
API_MAX_PAGE_SIZE = config('API_MAX_PAGE_SIZE', default=100, cast=int)

# Notifications
FCM_SERVER_KEY = config('FCM_SERVER_KEY', default='')
FCM_SENDER_ID = config('FCM_SENDER_ID', default='')
SMS_NOTIFICATION_ENABLED = config('SMS_NOTIFICATION_ENABLED', default=True, cast=bool)
SMS_NOTIFICATION_SENDER_ID = config('SMS_NOTIFICATION_SENDER_ID', default='NOTIFY')
EMAIL_NOTIFICATION_ENABLED = config('EMAIL_NOTIFICATION_ENABLED', default=True, cast=bool)
EMAIL_NOTIFICATION_FROM = config('EMAIL_NOTIFICATION_FROM', default='noreply@mifumo.com')

# Backups
BACKUP_ENABLED = config('BACKUP_ENABLED', default=True, cast=bool)
BACKUP_SCHEDULE = config('BACKUP_SCHEDULE', default='0 2 * * *')
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)
BACKUP_S3_BUCKET = config('BACKUP_S3_BUCKET', default='')

# Costs / Limits
MAX_MESSAGE_LENGTH = config('MAX_MESSAGE_LENGTH', default=160, cast=int)
MAX_BULK_MESSAGES = config('MAX_BULK_MESSAGES', default=1000, cast=int)
MAX_CONTACTS_PER_TENANT = config('MAX_CONTACTS_PER_TENANT', default=10000, cast=int)
SMS_COST_PER_MESSAGE = config('SMS_COST_PER_MESSAGE', default=0.05, cast=float)
WHATSAPP_COST_PER_MESSAGE = config('WHATSAPP_COST_PER_MESSAGE', default=0.01, cast=float)
FREE_MESSAGES_LIMIT = config('FREE_MESSAGES_LIMIT', default=100, cast=int)

# Defaults
DEFAULT_TIMEZONE = config('DEFAULT_TIMEZONE', default='Africa/Dar_es_Salaam')
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='USD')
DEFAULT_LANGUAGE = config('DEFAULT_LANGUAGE', default='en')

# =============================================================================
# CACHE (wired to your CACHE_* knobs)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mifumo-locmem',
        'TIMEOUT': config('CACHE_TTL', default=300, cast=int),
        'OPTIONS': {
            'MAX_ENTRIES': config('CACHE_MAX_ENTRIES', default=1000, cast=int),
            'CULL_FREQUENCY': config('CACHE_CULL_FREQUENCY', default=3, cast=int),
        }
    }
}

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = config('LOG_LEVEL', default='INFO')

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
    'root': {'handlers': ['console'], 'level': LOG_LEVEL},
    'loggers': {
        'django': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'mifumo': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else LOG_LEVEL, 'propagate': False},
    },
}

# =============================================================================
# SENTRY (optional, no warnings when DSN empty)
# =============================================================================
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN.strip():
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=True,
        )
    except Exception as e:
        import logging as _logging
        _logging.getLogger(__name__).warning(f"Failed to initialize Sentry: {e}")
        _logging.getLogger(__name__).warning("Continuing without Sentry monitoring")

# =============================================================================
# SECURITY HEADERS
# =============================================================================
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='DENY')

# =============================================================================
# JAZZMIN
# =============================================================================
JAZZMIN_SETTINGS = {
    "site_title": "Mifumo WMS Admin",
    "site_header": "Mifumo WMS",
    "site_brand": "Mifumo WMS",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to Mifumo WMS Admin Panel",
    "copyright": "Mifumo Labs",
    "search_model": ["auth.User", "accounts.User", "tenants.Tenant"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/swagger/", "new_window": True},
        {"model": "auth.User"},
        {"app": "messaging"},
    ],
    "usermenu_links": [
        {"name": "API Documentation", "url": "/swagger/", "new_window": True},
        {"name": "Support", "url": "https://github.com/mifumolabs/mifumoWMS", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "accounts", "tenants", "messaging", "billing"],
    "custom_links": {
        "messaging": [{
            "name": "SMS Management",
            "url": "/admin/messaging/smsprovider/",
            "icon": "fas fa-sms",
            "permissions": ["messaging.view_smsprovider"]
        }],
        "billing": [{
            "name": "Billing Overview",
            "url": "/admin/billing/subscription/",
            "icon": "fas fa-credit-card",
            "permissions": ["billing.view_subscription"]
        }]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.User": "fas fa-user-tie",
        "accounts.UserProfile": "fas fa-id-card",
        "tenants.Tenant": "fas fa-building",
        "tenants.Membership": "fas fa-user-plus",
        "messaging.Contact": "fas fa-address-book",
        "messaging.Segment": "fas fa-tags",
        "messaging.Template": "fas fa-file-alt",
        "messaging.Conversation": "fas fa-comments",
        "messaging.Message": "fas fa-envelope",
        "messaging.Campaign": "fas fa-bullhorn",
        "messaging.Flow": "fas fa-project-diagram",
        # SMS Group Icons
        "messaging.SMSProvider": "fas fa-server",
        "messaging.SMSSenderID": "fas fa-id-badge",
        "messaging.SMSMessage": "fas fa-paper-plane",
        "messaging.SMSTemplate": "fas fa-file-text",
        "messaging.SMSDeliveryReport": "fas fa-chart-line",
        "messaging.SMSBulkUpload": "fas fa-upload",
        "messaging.SMSSchedule": "fas fa-clock",
        "messaging.SenderNameRequest": "fas fa-user-plus",
        "billing.Plan": "fas fa-list-alt",
        "billing.Subscription": "fas fa-credit-card",
        "billing.Invoice": "fas fa-file-invoice",
        "billing.PaymentMethod": "fas fa-wallet",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
