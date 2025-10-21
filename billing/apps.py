"""
Billing app configuration.
"""
from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'
    verbose_name = 'Billing & SMS Packages'

    def ready(self):
        """Import signals when app is ready."""
        import billing.signals
