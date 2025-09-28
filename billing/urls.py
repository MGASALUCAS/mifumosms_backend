"""
URL patterns for billing functionality.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Plans
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    
    # Subscriptions
    path('subscription/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscription/create/', views.create_subscription, name='subscription-create'),
    path('subscription/cancel/', views.cancel_subscription, name='subscription-cancel'),
    
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/<uuid:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    
    # Payment Methods
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('payment-methods/<uuid:pk>/', views.PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    path('payment-methods/<uuid:payment_method_id>/set-default/', views.set_default_payment_method, name='payment-method-set-default'),
    
    # Usage
    path('usage/', views.UsageRecordListView.as_view(), name='usage-list'),
    path('usage/limits/', views.usage_limits, name='usage-limits'),
    
    # Billing Overview
    path('overview/', views.billing_overview, name='billing-overview'),
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/validate/', views.validate_coupon, name='coupon-validate'),
]
