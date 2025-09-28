# Mifumo WMS Backend

> **World-Class Django REST API for Multi-Tenant WhatsApp Messaging SaaS**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://djangoproject.com)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.14-red.svg)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.3+-green.svg)](https://celeryproject.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Overview

The Mifumo WMS Backend is a sophisticated, production-ready Django REST API that powers Africa's leading WhatsApp messaging platform for SMEs. Built with enterprise-grade architecture, it provides scalable multi-tenant messaging capabilities with AI-powered features.

### 🏗️ Architecture Highlights

- **Multi-Tenant Architecture**: Subdomain-based tenant isolation with complete data separation
- **Microservices-Ready**: Modular design with clear separation of concerns
- **Event-Driven**: Celery-based background task processing
- **AI-Integrated**: Hugging Face integration for smart responses and conversation analysis
- **Production-Grade**: Comprehensive logging, monitoring, and error handling

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Development Guide](#-development-guide)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended: 3.11.7)
- **PostgreSQL 15+** or **SQLite** (for development)
- **Redis 7+** (for Celery and caching)
- **Node.js 18+** (for frontend development)

### Installation

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/mifumolabs/mifumo-wms.git
   cd mifumo-wms/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py shell < seed_data.py
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Start Celery Worker** (in separate terminal)
   ```bash
   celery -A mifumo worker --loglevel=info
   ```

### 🎯 Quick Test

```bash
# Test API health
curl http://localhost:8000/api/health/

# Test authentication
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "first_name": "Test", "last_name": "User"}'
```

## 🏗️ Architecture

### Core Components

```
backend/
├── mifumo/                 # Django project settings
│   ├── settings.py         # Environment-based configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI application
├── core/                   # Core utilities and middleware
│   ├── middleware.py       # Custom middleware (tenant, logging)
│   ├── permissions.py     # Custom permission classes
│   └── rate_limits.py     # Rate limiting utilities
├── accounts/               # User management and authentication
│   ├── models.py          # User and UserProfile models
│   ├── serializers.py     # User serialization
│   ├── views.py           # Authentication views
│   └── urls.py            # Auth endpoints
├── tenants/                # Multi-tenancy management
│   ├── models.py          # Tenant model
│   ├── serializers.py     # Tenant serialization
│   └── views.py           # Tenant management
├── messaging/              # Core messaging functionality
│   ├── models.py          # Message, Contact, Conversation models
│   ├── models_sms.py      # SMS-specific models
│   ├── serializers.py     # Message serialization
│   ├── views.py           # Messaging views
│   ├── services/          # External service integrations
│   │   ├── whatsapp.py    # WhatsApp Business API
│   │   ├── sms_service.py # SMS provider integration
│   │   └── ai.py          # AI/ML services
│   └── tasks.py           # Celery background tasks
├── billing/                # Subscription and payment management
│   ├── models.py          # Billing models
│   ├── services/          # Payment processing
│   │   └── stripe_service.py
│   └── views.py           # Billing endpoints
└── api/                    # API utilities and documentation
    ├── schema.py          # OpenAPI schema
    └── urls.py            # API routing
```

### Database Schema

#### Core Models

- **User**: Custom user model with profile management
- **Tenant**: Multi-tenant organization model
- **Contact**: Customer contact information with opt-in/out tracking
- **Conversation**: Message thread management
- **Message**: Individual message with status tracking
- **Template**: Reusable message templates
- **Campaign**: Marketing campaign management
- **Flow**: Automated conversation flows

#### Key Features

- **UUID Primary Keys**: All models use UUID for better security
- **Soft Deletes**: Important data is never permanently deleted
- **Audit Trails**: Comprehensive created_at/updated_at tracking
- **JSON Fields**: Flexible data storage for dynamic attributes
- **Multi-Tenant Isolation**: Complete data separation per tenant

### API Design Principles

1. **RESTful Design**: Follows REST conventions with proper HTTP methods
2. **Consistent Response Format**: Standardized API response structure
3. **Comprehensive Error Handling**: Detailed error messages with proper HTTP status codes
4. **Pagination**: All list endpoints support pagination
5. **Filtering & Search**: Advanced filtering and search capabilities
6. **Rate Limiting**: Built-in rate limiting for API protection

## 📚 API Documentation

### Authentication

The API uses JWT (JSON Web Tokens) for authentication with refresh token support.

```python
# Login
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password123"
}

# Response
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### Core Endpoints

#### Messaging
- `GET /api/messaging/contacts/` - List contacts
- `POST /api/messaging/contacts/` - Create contact
- `GET /api/messaging/conversations/` - List conversations
- `POST /api/messaging/messages/` - Send message
- `GET /api/messaging/templates/` - List templates

#### Campaigns
- `GET /api/messaging/campaigns/` - List campaigns
- `POST /api/messaging/campaigns/` - Create campaign
- `POST /api/messaging/campaigns/{id}/start/` - Start campaign

#### Analytics
- `GET /api/messaging/analytics/overview/` - Dashboard statistics

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **OpenAPI JSON**: `http://localhost:8000/swagger.json`

## 🛠️ Development Guide

### Setting Up Development Environment

1. **Database Configuration**
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'mifumo_dev',
           'USER': 'postgres',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **Redis Configuration**
   ```python
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```

3. **Environment Variables**
   
   **🔐 IMPORTANT**: Copy the environment template and configure your secrets:
   ```bash
   # Copy the environment template
   cp environment_config.env .env
   
   # Edit with your actual values
   nano .env
   ```
   
   **📚 For detailed environment configuration, see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)**
   
   #### Quick Start - Required Variables
   ```bash
   # .env
   DJANGO_SECRET_KEY=your-super-secret-key-here
   DJANGO_DEBUG=False
   DATABASE_URL=postgres://user:password@localhost:5432/mifumo_wms
   REDIS_URL=redis://localhost:6379/0
   WA_PHONE_NUMBER_ID=your-phone-number-id
   WA_TOKEN=your-whatsapp-token
   WA_VERIFY_TOKEN=your-verify-token
   BEEM_API_KEY=your-beem-api-key
   BEEM_SECRET_KEY=your-beem-secret-key
   STRIPE_SECRET_KEY=sk_live_your-stripe-secret
   STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable
   STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
   ```
   
   **⚠️ Security Note**: Never commit your `.env` file to version control. The `.env` file is automatically ignored by git.

### Code Organization

#### Adding New Features

1. **Create Model** in appropriate app
2. **Create Serializer** for API representation
3. **Create ViewSet** with CRUD operations
4. **Add URL patterns** to app's urls.py
5. **Write Tests** for all functionality
6. **Update Documentation** with new endpoints

#### Example: Adding a New Model

```python
# models.py
class NewFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'new_features'
        ordering = ['-created_at']

# serializers.py
class NewFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewFeature
        fields = '__all__'

# views.py
class NewFeatureViewSet(viewsets.ModelViewSet):
    queryset = NewFeature.objects.all()
    serializer_class = NewFeatureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test messaging

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🚀 Deployment

### Production Environment

1. **Environment Setup**
   ```bash
   export DJANGO_SETTINGS_MODULE=mifumo.settings.production
   export DJANGO_SECRET_KEY=your-production-secret
   export DATABASE_URL=postgres://user:pass@host:5432/mifumo_prod
   ```

2. **Database Migration**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

3. **Start Services**
   ```bash
   # Start Gunicorn
   gunicorn mifumo.wsgi:application --bind 0.0.0.0:8000
   
   # Start Celery Worker
   celery -A mifumo worker --loglevel=info
   
   # Start Celery Beat
   celery -A mifumo beat --loglevel=info
   ```

### Docker Deployment

```bash
# Build image
docker build -t mifumo-backend .

# Run container
docker run -p 8000:8000 mifumo-backend
```

### Scaling Considerations

- **Horizontal Scaling**: Multiple Celery workers
- **Database**: Read replicas for read-heavy operations
- **Caching**: Redis clustering for high availability
- **Load Balancing**: Nginx with multiple backend instances

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | - | Yes |
| `DJANGO_DEBUG` | Debug mode | False | No |
| `DATABASE_URL` | Database connection string | sqlite:///db.sqlite3 | No |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 | No |
| `WA_PHONE_NUMBER_ID` | WhatsApp phone number ID | - | Yes |
| `WA_TOKEN` | WhatsApp access token | - | Yes |
| `HF_API_KEY` | Hugging Face API key | - | No |
| `STRIPE_SECRET_KEY` | Stripe secret key | - | Yes |

### Multi-Tenant Configuration

The system supports subdomain-based multi-tenancy:

```python
# settings.py
ALLOWED_HOSTS = ['.yourdomain.com', '.localhost']
MIDDLEWARE = [
    'core.middleware.TenantMiddleware',  # Must be early in middleware stack
    # ... other middleware
]
```

## 📊 Monitoring & Logging

### Logging Configuration

```python
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
}
```

### Health Checks

- **API Health**: `GET /api/health/`
- **Database Health**: `GET /api/health/db/`
- **Redis Health**: `GET /api/health/redis/`

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with proper tests
4. **Run tests**: `python manage.py test`
5. **Format code**: `black . && flake8 .`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Code Standards

- **Python**: Follow PEP 8 style guide
- **Django**: Follow Django best practices
- **API**: Follow RESTful design principles
- **Tests**: Maintain >90% code coverage
- **Documentation**: Update docs for all changes

### Pull Request Guidelines

- Clear description of changes
- Link to related issues
- Include tests for new functionality
- Update documentation
- Ensure all checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.mifumo.com](https://docs.mifumo.com)
- **Issues**: [GitHub Issues](https://github.com/mifumolabs/mifumo-wms/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mifumolabs/mifumo-wms/discussions)
- **Email**: [dev@mifumo.com](mailto:dev@mifumo.com)

## 🎯 Roadmap

- [ ] GraphQL API support
- [ ] WebSocket real-time updates
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Advanced AI features
- [ ] Mobile app API endpoints
- [ ] Third-party integrations

## 📱 SMS Integration

### Beem Africa SMS

The platform includes comprehensive SMS capabilities via Beem Africa:

- **📱 Single SMS**: Send individual messages
- **📤 Bulk SMS**: Send to multiple recipients  
- **⏰ Scheduled SMS**: Schedule messages for later delivery
- **📊 Delivery Tracking**: Monitor message status
- **💰 Cost Management**: Track SMS costs and usage
- **🔧 Phone Validation**: Validate phone number formats
- **🌍 Multi-Country Support**: Send to all African countries

### SMS API Documentation

**📚 Complete API Reference**: [BEEM_SMS_API_DOCUMENTATION.md](BEEM_SMS_API_DOCUMENTATION.md)

**🧪 Postman Collection**: [BEEM_SMS_Postman_Collection.json](BEEM_SMS_Postman_Collection.json)

**⚙️ Postman Environment**: [BEEM_SMS_Postman_Environment.json](BEEM_SMS_Postman_Environment.json)

### Quick SMS Test

```bash
# Test SMS connection
curl -X GET "http://localhost:8000/api/messaging/sms/sms/beem/test-connection/" \
  -H "Authorization: Bearer your-jwt-token"

# Send test SMS
curl -X POST "http://localhost:8000/api/messaging/sms/sms/beem/send/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from Mifumo WMS!",
    "recipients": ["255700000001"],
    "sender_id": "MIFUMO"
  }'
```

---

**Built with ❤️ for African SMEs by [Mifumo Labs](https://mifumolabs.com)**

*Empowering businesses across Africa with world-class messaging technology.*
