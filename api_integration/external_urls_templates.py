"""
External Templates API URLs.
"""
from django.urls import path
from . import external_views_templates

app_name = 'external_templates'

urlpatterns = [
    # Template endpoints
    path('', external_views_templates.list_templates, name='list_templates'),
    path('create/', external_views_templates.create_template, name='create_template'),
    path('<str:template_id>/', external_views_templates.get_template, name='get_template'),
    path('<str:template_id>/update/', external_views_templates.update_template, name='update_template'),
    path('<str:template_id>/delete/', external_views_templates.delete_template, name='delete_template'),
]

