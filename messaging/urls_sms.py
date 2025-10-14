"""
SMS-specific URL patterns for Mifumo WMS.
Optimized for frontend integration.
"""
from django.urls import path
from . import views_sms_beem

urlpatterns = [
    # Core SMS Operations (used by frontend)
    path('send/', views_sms_beem.send_sms, name='sms-send'),
    path('balance/', views_sms_beem.get_beem_balance, name='sms-balance'),
    path('stats/', views_sms_beem.get_sms_stats, name='sms-stats'),

    # SMS Utilities (used by frontend)
    path('validate-phone/', views_sms_beem.validate_phone_number, name='sms-validate-phone'),
    path('test-connection/', views_sms_beem.test_beem_connection, name='sms-test-connection'),
    path('<uuid:message_id>/status/', views_sms_beem.get_sms_delivery_status, name='sms-delivery-status'),
]
