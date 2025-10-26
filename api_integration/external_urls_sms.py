"""
External SMS API URLs following African's Talking and Beem Africa patterns.
"""
from django.urls import path
from . import sms_api

app_name = 'external_sms'

urlpatterns = [
    # SMS Endpoints (similar to African's Talking)
    path('send/', sms_api.send_sms, name='send_sms'),
    path('status/<str:message_id>/', sms_api.get_message_status, name='message_status'),
    path('delivery-reports/', sms_api.get_delivery_reports, name='delivery_reports'),
    path('balance/', sms_api.get_balance, name='balance'),
    
    # Additional endpoints for compatibility
    path('messages/', sms_api.get_delivery_reports, name='messages'),  # Alias for delivery-reports
    path('messages/<str:message_id>/', sms_api.get_message_status, name='message_detail'),
]