"""
Main API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for API viewsets
router = DefaultRouter()

urlpatterns = [
    # Include all app URLs
    path('', include('tenants.urls')),
    path('', include('accounts.urls')),
    path('', include('messaging.urls')),
    path('', include('billing.urls')),
]
