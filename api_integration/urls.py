"""
URL patterns for API integration system.
"""
from django.urls import path, include
from . import views
from . import dashboard_views
from . import simple_sms_test

app_name = 'api_integration'

# Internal API URLs (for managing integrations)
internal_urlpatterns = [
    # API Accounts
    path('accounts/', views.APIAccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<uuid:pk>/', views.APIAccountDetailView.as_view(), name='account-detail'),
    path('accounts/<uuid:account_id>/stats/', views.api_account_stats, name='account-stats'),
    
    # API Keys
    path('accounts/<uuid:account_id>/keys/', views.APIKeyListCreateView.as_view(), name='key-list-create'),
    path('keys/<uuid:pk>/', views.APIKeyDetailView.as_view(), name='key-detail'),
    path('keys/<uuid:key_id>/stats/', views.api_key_stats, name='key-stats'),
    path('keys/<uuid:key_id>/revoke/', views.revoke_api_key, name='key-revoke'),
    path('keys/<uuid:key_id>/regenerate/', views.regenerate_api_key, name='key-regenerate'),
    
    # Integrations
    path('accounts/<uuid:account_id>/integrations/', views.APIIntegrationListCreateView.as_view(), name='integration-list-create'),
    path('integrations/<uuid:pk>/', views.APIIntegrationDetailView.as_view(), name='integration-detail'),
    path('integrations/<uuid:integration_id>/stats/', views.integration_stats, name='integration-stats'),
]

# External API URLs (for integrations)
external_urlpatterns = [
    # Status and Info
    path('status/', views.external_api_status, name='external-status'),
    path('info/', views.external_api_info, name='external-info'),
    
    # SMS API
    path('sms/', include('api_integration.external_urls_sms')),
    
    # Simple SMS Test API (bypasses DRF authentication)
    path('test-sms/send/', simple_sms_test.test_sms_send, name='test-sms-send'),
    path('test-sms/status/<str:message_id>/', simple_sms_test.test_sms_status, name='test-sms-status'),
    path('test-sms/balance/', simple_sms_test.test_sms_balance, name='test-sms-balance'),
    
    # Contacts API (temporarily disabled due to missing functions)
    # path('contacts/', include('api_integration.external_urls_contacts')),
    
    # Campaigns API
    path('campaigns/', include('api_integration.external_urls_campaigns')),
    
    # Templates API
    path('templates/', include('api_integration.external_urls_templates')),
]

# Dashboard URLs (for UI)
dashboard_urlpatterns = [
    path('dashboard/', dashboard_views.api_dashboard, name='api_dashboard'),
    path('documentation/', dashboard_views.api_documentation, name='api_documentation'),
    path('usage-logs/', dashboard_views.api_usage_logs, name='api_usage_logs'),
    path('settings/', dashboard_views.api_settings, name='api_settings'),
    
    # AJAX endpoints
    path('keys/create/', dashboard_views.create_api_key, name='create_api_key'),
    path('keys/<uuid:key_id>/revoke/', dashboard_views.revoke_api_key, name='revoke_api_key'),
    path('keys/<uuid:key_id>/regenerate/', dashboard_views.regenerate_api_key, name='regenerate_api_key'),
    path('webhooks/create/', dashboard_views.create_webhook, name='create_webhook'),
    path('webhooks/<uuid:webhook_id>/toggle/', dashboard_views.toggle_webhook, name='toggle_webhook'),
    path('webhooks/<uuid:webhook_id>/delete/', dashboard_views.delete_webhook, name='delete_webhook'),
]

urlpatterns = [
    # Dashboard UI
    path('', include(dashboard_urlpatterns)),
    
    # Internal management API
    path('api/', include(internal_urlpatterns)),
    
    # External integration API
    path('v1/', include(external_urlpatterns)),
]

