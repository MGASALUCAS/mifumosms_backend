"""
SMS-specific URL patterns for Mifumo WMS.
"""
from django.urls import path
from . import views_sms, views_sms_beem

urlpatterns = [
    # SMS Providers
    path('sms/providers/', views_sms.SMSProviderListCreateView.as_view(), name='sms-provider-list-create'),
    path('sms/providers/<uuid:pk>/', views_sms.SMSProviderDetailView.as_view(), name='sms-provider-detail'),
    
    # SMS Sender IDs
    path('sms/sender-ids/', views_sms.SMSSenderIDListCreateView.as_view(), name='sms-sender-id-list-create'),
    path('sms/sender-ids/<uuid:pk>/', views_sms.SMSSenderIDDetailView.as_view(), name='sms-sender-id-detail'),
    
    # SMS Templates
    path('sms/templates/', views_sms.SMSTemplateListCreateView.as_view(), name='sms-template-list-create'),
    path('sms/templates/<uuid:pk>/', views_sms.SMSTemplateDetailView.as_view(), name='sms-template-detail'),
    
    # SMS Messages
    path('sms/messages/', views_sms.SMSMessageListView.as_view(), name='sms-message-list'),
    path('sms/delivery-reports/', views_sms.SMSDeliveryReportListView.as_view(), name='sms-delivery-report-list'),
    
    # SMS Bulk Operations
    path('sms/bulk-uploads/', views_sms.SMSBulkUploadListView.as_view(), name='sms-bulk-upload-list'),
    path('sms/send/', views_sms.send_sms_view, name='sms-send'),
    path('sms/send-bulk/', views_sms.send_bulk_sms_view, name='sms-send-bulk'),
    path('sms/upload-excel/', views_sms.upload_excel_sms_view, name='sms-upload-excel'),
    
    # SMS Schedules
    path('sms/schedules/', views_sms.SMSScheduleListCreateView.as_view(), name='sms-schedule-list-create'),
    path('sms/schedules/<uuid:pk>/', views_sms.SMSScheduleDetailView.as_view(), name='sms-schedule-detail'),
    
    # SMS Utilities
    path('sms/balance/', views_sms.sms_balance_view, name='sms-balance'),
    path('sms/stats/', views_sms.sms_stats_view, name='sms-stats'),
    path('sms/create-sender-id/', views_sms.create_sender_id_view, name='sms-create-sender-id'),
    path('sms/create-template/', views_sms.create_sms_template_view, name='sms-create-template'),
    
    # Beem SMS Integration
    path('sms/beem/send/', views_sms_beem.send_sms, name='sms-beem-send'),
    path('sms/beem/send-bulk/', views_sms_beem.send_bulk_sms, name='sms-beem-send-bulk'),
    path('sms/beem/test-connection/', views_sms_beem.test_beem_connection, name='sms-beem-test-connection'),
    path('sms/beem/balance/', views_sms_beem.get_beem_balance, name='sms-beem-balance'),
    path('sms/beem/validate-phone/', views_sms_beem.validate_phone_number, name='sms-beem-validate-phone'),
    path('sms/beem/<uuid:message_id>/status/', views_sms_beem.get_sms_delivery_status, name='sms-beem-delivery-status'),
]
