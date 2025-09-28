"""
OpenAPI schema configuration for Mifumo WMS API.
"""
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# API Info
api_info = openapi.Info(
    title="Mifumo WMS API",
    default_version='v1',
    description="""
    Multi-tenant WhatsApp messaging SaaS API for African SMEs.
    
    ## Features
    - Multi-tenant architecture with subdomain-based tenant resolution
    - WhatsApp Business Cloud API integration
    - AI-powered reply suggestions and conversation summaries
    - Campaign management and automation
    - Contact segmentation and management
    - Real-time messaging and webhooks
    - Stripe billing integration
    - Usage tracking and analytics
    
    ## Authentication
    This API uses JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ## Tenant Resolution
    The API automatically resolves tenants based on the request's subdomain or domain.
    For example:
    - `https://acme.mifumo.local/api/contacts/` → Tenant: acme
    - `https://acme.com/api/contacts/` → Tenant: acme (if domain is mapped)
    
    ## Rate Limiting
    API requests are rate limited per tenant and per user:
    - User rate limit: 100 requests per hour
    - Tenant rate limit: 1000 requests per hour
    - Message rate limit: 100 messages per minute per tenant
    
    ## Webhooks
    The API provides webhooks for real-time updates:
    - WhatsApp webhooks: `/webhooks/whatsapp/`
    - Stripe webhooks: `/webhooks/stripe/`
    """,
    terms_of_service="https://www.mifumo.com/terms/",
    contact=openapi.Contact(
        name="Mifumo Support",
        email="support@mifumo.com",
        url="https://www.mifumo.com/support"
    ),
    license=openapi.License(
        name="MIT License",
        url="https://opensource.org/licenses/MIT"
    ),
)

# Common response schemas
error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed error information'),
    }
)

validation_error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'field_name': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='List of validation errors for the field'
        )
    }
)

# Common parameters
tenant_header_param = openapi.Parameter(
    'X-Tenant',
    openapi.IN_HEADER,
    description='Tenant ID (alternative to subdomain-based resolution)',
    type=openapi.TYPE_STRING,
    required=False
)

# Common responses
common_responses = {
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        'Bad Request',
        validation_error_response_schema,
        examples={
            'application/json': {
                'field_name': ['This field is required.']
            }
        }
    ),
    status.HTTP_401_UNAUTHORIZED: openapi.Response(
        'Unauthorized',
        error_response_schema,
        examples={
            'application/json': {
                'error': 'Authentication credentials were not provided.'
            }
        }
    ),
    status.HTTP_403_FORBIDDEN: openapi.Response(
        'Forbidden',
        error_response_schema,
        examples={
            'application/json': {
                'error': 'You do not have permission to perform this action.'
            }
        }
    ),
    status.HTTP_404_NOT_FOUND: openapi.Response(
        'Not Found',
        error_response_schema,
        examples={
            'application/json': {
                'error': 'Not found.'
            }
        }
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response(
        'Too Many Requests',
        error_response_schema,
        examples={
            'application/json': {
                'error': 'Rate limit exceeded. Try again in 60 seconds.'
            }
        }
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
        'Internal Server Error',
        error_response_schema,
        examples={
            'application/json': {
                'error': 'An unexpected error occurred.'
            }
        }
    ),
}

# Pagination schema
pagination_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of items'),
        'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to next page'),
        'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to previous page'),
        'results': openapi.Schema(type=openapi.TYPE_ARRAY, description='List of items')
    }
)

# Contact schema
contact_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Contact ID'),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Contact name'),
        'phone_e164': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number in E.164 format'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email address'),
        'attributes': openapi.Schema(type=openapi.TYPE_OBJECT, description='Custom attributes'),
        'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='Contact tags'),
        'is_opted_in': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether contact has opted in'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Creation timestamp'),
    }
)

# Message schema
message_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Message ID'),
        'conversation': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Conversation ID'),
        'direction': openapi.Schema(type=openapi.TYPE_STRING, enum=['in', 'out'], description='Message direction'),
        'provider': openapi.Schema(type=openapi.TYPE_STRING, enum=['whatsapp', 'sms', 'telegram'], description='Message provider'),
        'text': openapi.Schema(type=openapi.TYPE_STRING, description='Message text'),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['queued', 'sent', 'delivered', 'read', 'failed'], description='Message status'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Creation timestamp'),
    }
)

# Campaign schema
campaign_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='Campaign ID'),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Campaign name'),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'scheduled', 'running', 'completed', 'cancelled'], description='Campaign status'),
        'total_contacts': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of contacts'),
        'sent_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of messages sent'),
        'delivered_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of messages delivered'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Creation timestamp'),
    }
)
