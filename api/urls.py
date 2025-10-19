"""
Main API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for API viewsets
router = DefaultRouter()

urlpatterns = [
    # All app URLs are included in mifumo/urls.py with proper prefixes
    # This file is kept for potential future API router configurations
]
