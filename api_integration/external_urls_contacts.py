"""
External Contacts API URLs.
"""
from django.urls import path
from . import external_views_contacts

app_name = 'external_contacts'

urlpatterns = [
    # Contact endpoints
    path('', external_views_contacts.list_contacts, name='list_contacts'),
    path('create/', external_views_contacts.create_contact, name='create_contact'),
    path('<str:contact_id>/', external_views_contacts.get_contact, name='get_contact'),
    path('<str:contact_id>/update/', external_views_contacts.update_contact, name='update_contact'),
    path('<str:contact_id>/delete/', external_views_contacts.delete_contact, name='delete_contact'),
    path('search/', external_views_contacts.search_contacts, name='search_contacts'),
    
    # Segment endpoints
    path('segments/', external_views_contacts.list_segments, name='list_segments'),
    path('segments/create/', external_views_contacts.create_segment, name='create_segment'),
    path('segments/<str:segment_id>/', external_views_contacts.get_segment, name='get_segment'),
    path('segments/<str:segment_id>/update/', external_views_contacts.update_segment, name='update_segment'),
    path('segments/<str:segment_id>/delete/', external_views_contacts.delete_segment, name='delete_segment'),
]