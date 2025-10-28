"""
SMS Provider API URLs - Simple integration endpoints.
"""
from django.urls import path
from . import sms_provider_api

app_name = 'sms_provider'

urlpatterns = [
    # Registration
    path('register/', sms_provider_api.register_sms_provider, name='register'),
    
    # SMS Operations
    path('send/', sms_provider_api.send_sms, name='send-sms'),
    path('status/<uuid:message_id>/', sms_provider_api.get_message_status, name='message-status'),
    path('reports/', sms_provider_api.get_delivery_reports, name='delivery-reports'),
    
    # Account Info
    path('info/', sms_provider_api.get_api_info, name='api-info'),
]







