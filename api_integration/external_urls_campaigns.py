"""
External Campaigns API URLs.
"""
from django.urls import path
from . import external_views_campaigns

app_name = 'external_campaigns'

urlpatterns = [
    # Campaign endpoints
    path('', external_views_campaigns.list_campaigns, name='list_campaigns'),
    path('create/', external_views_campaigns.create_campaign, name='create_campaign'),
    path('<str:campaign_id>/', external_views_campaigns.get_campaign, name='get_campaign'),
    path('<str:campaign_id>/update/', external_views_campaigns.update_campaign, name='update_campaign'),
    path('<str:campaign_id>/delete/', external_views_campaigns.delete_campaign, name='delete_campaign'),
    path('<str:campaign_id>/start/', external_views_campaigns.start_campaign, name='start_campaign'),
    path('<str:campaign_id>/stop/', external_views_campaigns.stop_campaign, name='stop_campaign'),
]