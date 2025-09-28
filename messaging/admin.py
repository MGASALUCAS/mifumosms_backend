"""
Admin configuration for messaging models.
"""
from django.contrib import admin
from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_e164', 'email', 'is_active', 'is_opted_in', 'created_at']
    list_filter = ['is_active', 'opt_in_at', 'opt_out_at', 'created_at']
    search_fields = ['name', 'phone_e164', 'email']
    readonly_fields = ['created_at', 'updated_at', 'last_contacted_at']
    raw_id_fields = ['tenant']


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['contact_count', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'created_by']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'language', 'approved', 'usage_count', 'created_at']
    list_filter = ['category', 'language', 'approved', 'created_at']
    search_fields = ['name', 'body_text']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'created_by']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['contact', 'status', 'message_count', 'unread_count', 'last_message_at']
    list_filter = ['status', 'created_at', 'last_message_at']
    search_fields = ['contact__name', 'contact__phone_e164', 'subject']
    readonly_fields = ['message_count', 'unread_count', 'created_at', 'updated_at', 'last_message_at', 'closed_at']
    raw_id_fields = ['tenant', 'contact']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'direction', 'provider', 'status', 'created_at']
    list_filter = ['direction', 'provider', 'status', 'created_at']
    search_fields = ['text', 'conversation__contact__name']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    raw_id_fields = ['tenant', 'conversation', 'template', 'created_by']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['message', 'file_name', 'file_type', 'file_size', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['message']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_contacts', 'sent_count', 'created_at']
    list_filter = ['status', 'created_at', 'schedule_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'total_contacts', 'sent_count', 'delivered_count', 'read_count', 'failed_count',
        'started_at', 'completed_at', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['tenant', 'template', 'segment', 'created_by']


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'trigger_count', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['trigger_count', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'created_by']
