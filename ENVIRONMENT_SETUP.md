# 🔐 Environment Configuration Guide

This guide explains how to properly configure the Mifumo WMS backend with environment variables for maximum security and flexibility.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Environment Variables Reference](#environment-variables-reference)
- [Security Best Practices](#security-best-practices)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Copy Environment Template

```bash
# Copy the environment template
cp environment_config.env .env

# Edit with your actual values
nano .env
```

### 2. Required Variables

At minimum, you must configure these variables:

```env
# Django Core
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@localhost:5432/mifumo_wms

# Redis
REDIS_URL=redis://localhost:6379/0

# WhatsApp Business API
WA_PHONE_NUMBER_ID=your-phone-number-id
WA_TOKEN=your-whatsapp-token
WA_VERIFY_TOKEN=your-verify-token

# SMS Provider (Beem Africa)
BEEM_API_KEY=your-beem-api-key
BEEM_SECRET_KEY=your-beem-secret-key

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

### 3. Test Configuration

```bash
# Check if all required variables are set
python manage.py check --deploy

# Run the application
python manage.py runserver
```

## 📚 Environment Variables Reference

### 🔧 Django Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-change-me` | ✅ |
| `DJANGO_DEBUG` | Enable debug mode | `True` | ❌ |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `.localhost,.mifumo.local` | ✅ |

### 🗄️ Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` | ✅ |
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` | ❌ |
| `DB_NAME` | Database name | `mifumo_wms` | ❌ |
| `DB_USER` | Database user | `mifumo_user` | ❌ |
| `DB_PASSWORD` | Database password | `mifumo_password` | ❌ |
| `DB_HOST` | Database host | `localhost` | ❌ |
| `DB_PORT` | Database port | `5432` | ❌ |

### 🔴 Redis Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | ✅ |
| `REDIS_HOST` | Redis host | `localhost` | ❌ |
| `REDIS_PORT` | Redis port | `6379` | ❌ |
| `REDIS_DB` | Redis database number | `0` | ❌ |
| `REDIS_PASSWORD` | Redis password | - | ❌ |

### 📱 WhatsApp Business API

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WA_PHONE_NUMBER_ID` | WhatsApp phone number ID | - | ✅ |
| `WA_TOKEN` | WhatsApp access token | - | ✅ |
| `WA_VERIFY_TOKEN` | Webhook verification token | - | ✅ |
| `WA_API_BASE` | WhatsApp API base URL | `https://graph.facebook.com/v20.0` | ❌ |

### 📨 SMS Providers

#### Beem Africa (Primary)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BEEM_API_KEY` | Beem API key | - | ✅ |
| `BEEM_SECRET_KEY` | Beem secret key | - | ✅ |
| `BEEM_DEFAULT_SENDER_ID` | Default sender ID | `MIFUMO` | ❌ |
| `BEEM_API_TIMEOUT` | API timeout in seconds | `30` | ❌ |
| `BEEM_API_BASE_URL` | Beem API base URL | `https://apisms.beem.africa/v1` | ❌ |

#### Twilio (Optional)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio account SID | - | ❌ |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | - | ❌ |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | - | ❌ |

### 🤖 AI Services

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HF_API_URL` | Hugging Face API URL | `https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct` | ❌ |
| `HF_API_KEY` | Hugging Face API key | - | ❌ |
| `OPENAI_API_KEY` | OpenAI API key | - | ❌ |
| `OPENAI_MODEL` | OpenAI model | `gpt-3.5-turbo` | ❌ |

### 💳 Billing & Payments

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `STRIPE_SECRET_KEY` | Stripe secret key | - | ✅ |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - | ✅ |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | - | ✅ |

### 📧 Email Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` | ❌ |
| `EMAIL_PORT` | SMTP port | `587` | ❌ |
| `EMAIL_USE_TLS` | Use TLS | `True` | ❌ |
| `EMAIL_HOST_USER` | SMTP username | - | ❌ |
| `EMAIL_HOST_PASSWORD` | SMTP password | - | ❌ |
| `EMAIL_FROM_NAME` | From name | `Mifumo WMS` | ❌ |
| `EMAIL_FROM_ADDRESS` | From email | `noreply@mifumo.com` | ❌ |

### 🔒 Security Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://127.0.0.1:3000` | ❌ |
| `CORS_ALLOW_CREDENTIALS` | Allow credentials | `True` | ❌ |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `False` | ❌ |
| `SESSION_COOKIE_HTTPONLY` | HTTP-only session cookies | `True` | ❌ |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `False` | ❌ |
| `CSRF_COOKIE_HTTPONLY` | HTTP-only CSRF cookies | `True` | ❌ |

### 🔔 Webhook Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEBHOOK_SECRET_WHATSAPP` | WhatsApp webhook secret | - | ❌ |
| `WEBHOOK_SECRET_STRIPE` | Stripe webhook secret | - | ❌ |
| `WEBHOOK_SECRET_SMS` | SMS webhook secret | - | ❌ |

### 🏢 Business Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `COMPANY_NAME` | Company name | `Mifumo Labs` | ❌ |
| `COMPANY_EMAIL` | Company email | `hello@mifumo.com` | ❌ |
| `COMPANY_PHONE` | Company phone | `+255700000000` | ❌ |
| `COMPANY_ADDRESS` | Company address | `Dar es Salaam, Tanzania` | ❌ |
| `SUPPORT_EMAIL` | Support email | `support@mifumo.com` | ❌ |
| `SUPPORT_PHONE` | Support phone | `+255700000001` | ❌ |

### 🚩 Feature Flags

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_AI_FEATURES` | Enable AI features | `True` | ❌ |
| `ENABLE_SMS_FEATURES` | Enable SMS features | `True` | ❌ |
| `ENABLE_WHATSAPP_FEATURES` | Enable WhatsApp features | `True` | ❌ |
| `ENABLE_BILLING_FEATURES` | Enable billing features | `True` | ❌ |
| `ENABLE_ANALYTICS` | Enable analytics | `True` | ❌ |
| `ENABLE_WEBHOOKS` | Enable webhooks | `True` | ❌ |

## 🔐 Security Best Practices

### 1. Secret Management

```bash
# Generate a strong secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Use different secrets for different environments
# Development: Use weak secrets for convenience
# Staging: Use strong secrets similar to production
# Production: Use the strongest possible secrets
```

### 2. Environment Separation

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

### 3. File Permissions

```bash
# Set restrictive permissions on .env file
chmod 600 .env

# Ensure only the application user can read it
chown app:app .env
```

### 4. Never Commit Secrets

```bash
# Add .env to .gitignore
echo ".env" >> .gitignore

# Verify .env is not tracked
git status --ignored
```

### 5. Use Environment-Specific Values

```env
# Development
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///dev.db

# Production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=super-secure-production-key
DATABASE_URL=postgres://user:password@prod-db:5432/mifumo_wms
```

## 🚀 Production Deployment

### 1. Environment Variables

```bash
# Set environment variables in your deployment platform
# Heroku
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgres://...

# Docker
docker run -e DJANGO_SECRET_KEY=your-secret-key mifumo-wms

# Kubernetes
kubectl create secret generic mifumo-secrets --from-env-file=.env
```

### 2. Security Headers

```env
# Production security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. Database Security

```env
# Use SSL for database connections
DATABASE_URL=postgres://user:password@host:5432/db?sslmode=require

# Use connection pooling
DATABASE_CONN_MAX_AGE=600
```

### 4. Monitoring

```env
# Enable monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=WARNING
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Missing Environment Variables

```bash
# Check if variables are loaded
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DJANGO_SECRET_KEY)
```

#### 2. Database Connection Issues

```bash
# Test database connection
python manage.py dbshell

# Check database settings
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
```

#### 3. Redis Connection Issues

```bash
# Test Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

#### 4. WhatsApp API Issues

```bash
# Test WhatsApp configuration
python manage.py shell
>>> from messaging.services.whatsapp import WhatsAppService
>>> service = WhatsAppService()
>>> print(service.phone_number_id)
```

### Debug Mode

```env
# Enable debug mode for troubleshooting
DJANGO_DEBUG=True
LOG_LEVEL=DEBUG
```

### Logging

```python
# Add to settings.py for detailed logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## 📞 Support

If you encounter issues with environment configuration:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [security best practices](#security-best-practices)
3. Contact support at support@mifumo.com

## 🔄 Updates

This configuration guide is regularly updated. Check the changelog for the latest changes.

---

**⚠️ Important**: Never commit your `.env` file to version control. Always use the `.env.example` file as a template.
