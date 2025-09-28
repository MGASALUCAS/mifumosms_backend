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
    'jazzmin',  # Must be before django.contrib.admin
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

# =============================================================================
# JAZZMIN CONFIGURATION - WORLD-CLASS ADMIN UI
# =============================================================================

JAZZMIN_SETTINGS = {
    # Title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Mifumo WMS Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Mifumo WMS",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Mifumo WMS",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": None,

    # Logo to use for your site, must be present in static files, used for login form logo (if site_logo is not provided)
    "login_logo": None,

    # Logo to use for login form in dark themes (if login_logo is not provided)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,

    # Welcome text on the login screen
    "welcome_sign": "Welcome to Mifumo WMS Admin Panel",

    # Copyright on the footer
    "copyright": "Mifumo Labs",

    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": ["auth.User", "accounts.User", "tenants.Tenant"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu before the "Logout" link
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "API Docs", "url": "/swagger/", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "messaging"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "API Documentation", "url": "/swagger/", "new_window": True},
        {"name": "Support", "url": "https://github.com/mifumolabs/mifumoWMS", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "accounts", "tenants", "messaging", "billing"],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "messaging": [{
            "name": "SMS Dashboard",
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

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free
    # for the full list of 5.13.0 free icon classes
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
        "messaging.SMSProvider": "fas fa-sms",
        "messaging.SenderID": "fas fa-id-badge",
        "messaging.SMSTemplate": "fas fa-file-text",
        "messaging.SMSMessage": "fas fa-sms",
        "billing.Plan": "fas fa-list-alt",
        "billing.Subscription": "fas fa-credit-card",
        "billing.Invoice": "fas fa-file-invoice",
        "billing.PaymentMethod": "fas fa-wallet",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    # Add a language dropdown into the admin
    "language_chooser": False,
}

# Jazzmin UI Builder Configuration
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
