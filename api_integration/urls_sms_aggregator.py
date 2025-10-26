"""
SMS Aggregator API URLs - Multi-network SMS routing service.
"""
from django.urls import path
from . import simple_sms_aggregator

app_name = 'sms_aggregator'

urlpatterns = [
    # Registration
    path('register/', simple_sms_aggregator.register_sms_aggregator_user, name='register'),
    
    # SMS Operations
    path('send/', simple_sms_aggregator.send_aggregated_sms, name='send-sms'),
    path('status/<uuid:message_id>/', simple_sms_aggregator.get_message_status, name='message-status'),
    path('reports/', simple_sms_aggregator.get_delivery_reports, name='delivery-reports'),
    
    # Network Information
    path('coverage/', simple_sms_aggregator.get_network_coverage, name='network-coverage'),
    path('info/', simple_sms_aggregator.get_api_info, name='api-info'),
]
