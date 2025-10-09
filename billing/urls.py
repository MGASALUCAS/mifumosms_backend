"""
URL patterns for billing functionality.
Optimized for frontend integration.
"""
from django.urls import path
from . import views, views_sms

urlpatterns = [
    # Core billing endpoints (used by frontend)
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('subscription/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('usage/', views.UsageRecordListView.as_view(), name='usage-list'),
    path('overview/', views.billing_overview, name='billing-overview'),
    
    # SMS billing endpoints
    path('sms/packages/', views_sms.SMSPackageListView.as_view(), name='sms-package-list'),
    path('sms/balance/', views_sms.SMSBalanceView.as_view(), name='sms-balance'),
    path('sms/purchase/', views_sms.create_purchase, name='sms-purchase-create'),
    path('sms/purchases/', views_sms.PurchaseListView.as_view(), name='sms-purchase-list'),
    path('sms/purchases/history/', views_sms.purchase_history, name='sms-purchase-history'),
    path('sms/purchases/<uuid:pk>/', views_sms.PurchaseDetailView.as_view(), name='sms-purchase-detail'),
    path('sms/purchases/<uuid:purchase_id>/complete/', views_sms.complete_purchase, name='sms-purchase-complete'),
    path('sms/usage/statistics/', views_sms.usage_statistics, name='sms-usage-statistics'),
]
