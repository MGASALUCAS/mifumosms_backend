"""
URL patterns for billing functionality.
Optimized for frontend integration.
"""
from django.urls import path
from . import views, views_sms, views_payment, views_billing_history

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
    
    # ZenoPay Payment Gateway endpoints
    path('payments/initiate/', views_payment.initiate_payment, name='payment-initiate'),
    path('payments/verify/<str:order_id>/', views_payment.verify_payment, name='payment-verify'),
    path('payments/active/', views_payment.get_active_payments, name='payment-active'),
    path('payments/cleanup/', views_payment.cleanup_payments, name='payment-cleanup'),
    path('payments/transactions/', views_payment.PaymentTransactionListView.as_view(), name='payment-transaction-list'),
    path('payments/transactions/<uuid:transaction_id>/', views_payment.PaymentTransactionDetailView.as_view(), name='payment-transaction-detail'),
    path('payments/transactions/<uuid:transaction_id>/status/', views_payment.check_payment_status, name='payment-status-check'),
    path('payments/sync/', views_payment.sync_pending_payments, name='payment-sync'),
    path('payments/transactions/<uuid:transaction_id>/progress/', views_payment.payment_progress, name='payment-progress'),
    path('payments/transactions/<uuid:transaction_id>/cancel/', views_payment.cancel_payment, name='payment-cancel'),
    path('payments/webhook/', views_payment.payment_webhook, name='payment-webhook'),
    
    # Mobile money providers endpoint
    path('payments/providers/', views_payment.get_mobile_money_providers, name='payment-providers'),
    
    # Custom SMS purchase endpoints
    path('payments/custom-sms/calculate/', views_payment.calculate_custom_sms_pricing, name='custom-sms-calculate'),
    path('payments/custom-sms/initiate/', views_payment.initiate_custom_sms_purchase, name='custom-sms-initiate'),
    path('payments/custom-sms/<uuid:purchase_id>/status/', views_payment.check_custom_sms_purchase_status, name='custom-sms-status'),
    
    # Billing history endpoints
    path('history/', views_billing_history.BillingHistoryView.as_view(), name='billing-history'),
    path('history/summary/', views_billing_history.billing_history_summary, name='billing-history-summary'),
    path('history/purchases/', views_billing_history.purchase_history_detailed, name='purchase-history-detailed'),
    path('history/payments/', views_billing_history.payment_history_detailed, name='payment-history-detailed'),
    path('history/usage/', views_billing_history.usage_history_detailed, name='usage-history-detailed'),
    path('history/comprehensive/', views_billing_history.comprehensive_transaction_history, name='comprehensive-transaction-history'),
]
