"""
Views for messaging functionality.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.db.models import JSONField

from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)
from .serializers import (
    ContactSerializer, ContactCreateSerializer, ContactBulkImportSerializer, ContactImportSerializer,
    ContactBulkEditSerializer, ContactBulkDeleteSerializer,
    SegmentSerializer, SegmentCreateSerializer,
    TemplateSerializer, TemplateCreateSerializer, TemplateUpdateSerializer, 
    TemplateDetailSerializer, TemplateListSerializer, TemplateFilterSerializer,
    ConversationSerializer, MessageSerializer, MessageCreateSerializer,
    CampaignSerializer, CampaignCreateSerializer,
    FlowSerializer, FlowCreateSerializer,
    ConversationSummarySerializer, AISuggestionsSerializer,
    PurchaseHistorySerializer, PurchaseHistorySummarySerializer
)
from core.permissions import IsTenantMember, IsTenantAdmin
from core.rate_limits import check_rate_limit, MESSAGE_RATE_LIMITER
from .tasks import send_message_task, ai_suggest_reply_task, ai_summarize_conversation_task
from .models_sms import SMSSenderID


def validate_user_tenant(user):
    """Validate that user has a valid tenant."""
    if not user.is_authenticated:
        raise ValueError('User is not authenticated')
    if not hasattr(user, 'tenant') or not user.tenant:
        raise ValueError('User does not have an associated tenant')


def get_tenant_queryset(model_class, user, **filters):
    """Get a queryset filtered by user and tenant, handling anonymous users."""
    if not user.is_authenticated:
        return model_class.objects.none()

    # Check if the model has a tenant field
    if hasattr(model_class, '_meta') and 'tenant' in [field.name for field in model_class._meta.fields]:
        # Model has tenant field - require tenant
        if not hasattr(user, 'tenant') or not user.tenant:
            return model_class.objects.none()
        return model_class.objects.filter(
            created_by=user,
            tenant=user.tenant,
            **filters
        )
    else:
        # For models without tenant field, only filter by created_by
        # This works for users with or without tenants
        return model_class.objects.filter(
            created_by=user,
            **filters
        )


class ContactFilterSet(FilterSet):
    """Custom filter set for Contact model to handle JSONField filtering."""

    class Meta:
        model = Contact
        fields = ['name', 'phone_e164', 'email', 'is_active', 'opt_in_at', 'opt_out_at']
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class ContactListCreateView(generics.ListCreateAPIView):
    """List and create contacts."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactFilterSet
    search_fields = ['name', 'phone_e164', 'email']
    ordering_fields = ['name', 'created_at', 'last_contacted_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactSerializer

    def get_queryset(self):
        """Filter contacts by user and tenant."""
        return get_tenant_queryset(Contact, self.request.user)

    def perform_create(self, serializer):
        """Create contact for the current user."""
        serializer.save(
            created_by=self.request.user,
            tenant=getattr(self.request.user, 'tenant', None)
        )


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a contact."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def get_queryset(self):
        """Filter contacts by user and tenant."""
        return get_tenant_queryset(Contact, self.request.user)


class ContactBulkImportView(generics.GenericAPIView):
    """Bulk import contacts from CSV/Excel or phone contacts."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactBulkImportSerializer

    def post(self, request, *args, **kwargs):
        """Import contacts from CSV/Excel data or phone contacts."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        import_type = serializer.validated_data.get('import_type', 'csv')
        skip_duplicates = serializer.validated_data.get('skip_duplicates', True)
        update_existing = serializer.validated_data.get('update_existing', False)

        if import_type == 'phone_contacts':
            return self._import_phone_contacts(serializer.validated_data, request)
        else:
            return self._import_csv_excel(serializer.validated_data, request)

    def _import_phone_contacts(self, validated_data, request):
        """Import contacts from phone contact picker."""
        contacts_data = validated_data['contacts']
        skip_duplicates = validated_data.get('skip_duplicates', True)
        update_existing = validated_data.get('update_existing', False)
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for i, contact_data in enumerate(contacts_data):
            try:
                phone = contact_data.get('phone')
                
                # Check for existing contact if phone is provided
                existing_contact = None
                if phone and skip_duplicates:
                    existing_contact = Contact.objects.filter(
                        phone_e164=phone,
                        created_by=request.user,
                        tenant=request.user.tenant
                    ).first()

                if existing_contact:
                    if update_existing:
                        # Update existing contact
                        existing_contact.name = contact_data['full_name'] or existing_contact.name
                        existing_contact.email = contact_data.get('email', '') or existing_contact.email
                        existing_contact.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                    continue

                # Create new contact
                contact_serializer_data = {
                    'name': contact_data['full_name'] or 'Unknown',
                    'phone_e164': phone,
                    'email': contact_data.get('email', ''),
                }

                contact_serializer = ContactCreateSerializer(data=contact_serializer_data)
                if contact_serializer.is_valid():
                    contact_serializer.save(
                        created_by=request.user,
                        tenant=request.user.tenant
                    )
                    imported_count += 1
                else:
                    errors.append(f"Contact {i+1}: {contact_serializer.errors}")

            except Exception as e:
                errors.append(f"Contact {i+1}: {str(e)}")

        response_data = {
            'success': True,
            'imported': imported_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total_processed': len(contacts_data),
            'errors': errors
        }

        if errors:
            response_data['message'] = f'Imported {imported_count}, updated {updated_count}, skipped {skipped_count} contacts with {len(errors)} errors'
        else:
            response_data['message'] = f'Successfully imported {imported_count}, updated {updated_count}, skipped {skipped_count} contacts'

        return Response(response_data, status=status.HTTP_201_CREATED)

    def _import_csv_excel(self, validated_data, request):
        """Import contacts from CSV/Excel data."""
        csv_data = validated_data.get('csv_data')
        file = validated_data.get('file')
        skip_duplicates = validated_data.get('skip_duplicates', True)
        update_existing = validated_data.get('update_existing', False)

        # Handle file upload
        if file and not csv_data:
            try:
                # Read file content
                if file.name.endswith('.csv'):
                    csv_data = file.read().decode('utf-8')
                elif file.name.endswith(('.xlsx', '.xls')):
                    # Handle Excel files
                    import pandas as pd
                    df = pd.read_excel(file)
                    csv_data = df.to_csv(index=False)
                else:
                    return Response({
                        'success': False,
                        'message': 'Unsupported file format. Please use CSV or Excel files.',
                        'imported_count': 0,
                        'errors': ['Unsupported file format']
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Error reading file',
                    'imported_count': 0,
                    'errors': [f'File reading error: {str(e)}']
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validate CSV data is not empty
        if not csv_data or not csv_data.strip():
            return Response({
                'success': False,
                'message': 'CSV data cannot be empty',
                'imported_count': 0,
                'errors': ['Empty CSV data provided']
            }, status=status.HTTP_400_BAD_REQUEST)

        imported_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        import csv
        from io import StringIO

        try:
            csv_reader = csv.DictReader(StringIO(csv_data))
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Invalid CSV format',
                'imported_count': 0,
                'errors': [f'CSV parsing error: {str(e)}']
            }, status=status.HTTP_400_BAD_REQUEST)

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            try:
                phone = row['phone_e164'].strip()
                
                # Check for existing contact if skip_duplicates is enabled
                existing_contact = None
                if skip_duplicates and phone:
                    existing_contact = Contact.objects.filter(
                        phone_e164=phone,
                        created_by=request.user,
                        tenant=request.user.tenant
                    ).first()

                if existing_contact:
                    if update_existing:
                        # Update existing contact
                        existing_contact.name = row['name'].strip()
                        existing_contact.email = row.get('email', '').strip() or existing_contact.email
                        if row.get('tags'):
                            existing_contact.tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip()]
                        existing_contact.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                    continue

                # Create new contact
                contact_data = {
                    'name': row['name'].strip(),
                    'phone_e164': phone,
                    'email': row.get('email', '').strip(),
                    'tags': row.get('tags', '').split(',') if row.get('tags') else [],
                    'attributes': {}
                }

                # Parse additional attributes
                for key, value in row.items():
                    if key not in ['name', 'phone_e164', 'email', 'tags'] and value.strip():
                        contact_data['attributes'][key] = value.strip()

                contact_serializer = ContactCreateSerializer(data=contact_data)
                if contact_serializer.is_valid():
                    contact_serializer.save(
                        created_by=request.user,
                        tenant=request.user.tenant
                    )
                    imported_count += 1
                else:
                    errors.append(f"Row {row_num}: {contact_serializer.errors}")

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        response_data = {
            'success': True,
            'imported': imported_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total_processed': imported_count + updated_count + skipped_count,
            'errors': errors
        }

        if errors:
            response_data['message'] = f'Imported {imported_count}, updated {updated_count}, skipped {skipped_count} contacts with {len(errors)} errors'
        else:
            response_data['message'] = f'Successfully imported {imported_count}, updated {updated_count}, skipped {skipped_count} contacts'

        return Response(response_data, status=status.HTTP_201_CREATED)


class ContactImportView(generics.GenericAPIView):
    """Import contacts from phone contact picker."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactImportSerializer

    def post(self, request, *args, **kwargs):
        """Import contacts from phone contact picker data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contacts_data = serializer.validated_data['contacts']
        imported_count = 0
        skipped_count = 0
        errors = []

        for i, contact_data in enumerate(contacts_data):
            try:
                # Check if contact already exists by phone number
                if contact_data.get('phone'):
                    existing_contact = Contact.objects.filter(
                        phone_e164=contact_data['phone'],
                        created_by=request.user
                    ).first()

                    if existing_contact:
                        skipped_count += 1
                        continue

                # Create contact data for serializer
                contact_serializer_data = {
                    'name': contact_data['full_name'] or 'Unknown',
                    'phone_e164': contact_data['phone'],
                    'email': contact_data.get('email', ''),
                }

                # Validate and create contact
                contact_serializer = ContactCreateSerializer(data=contact_serializer_data)
                if contact_serializer.is_valid():
                    contact_serializer.save(created_by=request.user)
                    imported_count += 1
                else:
                    errors.append(f"Contact {i+1}: {contact_serializer.errors}")

            except Exception as e:
                errors.append(f"Contact {i+1}: {str(e)}")

        response_data = {
            'imported': imported_count,
            'skipped': skipped_count,
            'total_processed': len(contacts_data),
            'errors': errors
        }

        if errors:
            response_data['message'] = f'Imported {imported_count} contacts, skipped {skipped_count} duplicates, {len(errors)} errors'
        else:
            response_data['message'] = f'Successfully imported {imported_count} contacts'

        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_opt_in(request, contact_id):
    """Opt in a contact."""
    contact = get_object_or_404(
        Contact,
        id=contact_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    contact.opt_in()

    return Response({'message': 'Contact opted in successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_opt_out(request, contact_id):
    """Opt out a contact."""
    contact = get_object_or_404(
        Contact,
        id=contact_id,
        created_by=request.user,
        tenant=request.user.tenant
    )

    # Validate reason is not too long
    reason = request.data.get('reason', '')
    if len(reason) > 500:  # Assuming max length from model
        return Response({
            'error': 'Reason cannot exceed 500 characters'
        }, status=status.HTTP_400_BAD_REQUEST)

    contact.opt_out(reason)

    return Response({'message': 'Contact opted out successfully'})


class ContactBulkEditView(generics.GenericAPIView):
    """Bulk edit contacts."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactBulkEditSerializer

    def post(self, request, *args, **kwargs):
        """Bulk edit multiple contacts."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact_ids = serializer.validated_data['contact_ids']
        updates = serializer.validated_data['updates']

        # Get contacts that belong to the user
        contacts = Contact.objects.filter(
            id__in=contact_ids,
            created_by=request.user,
            tenant=request.user.tenant
        )

        if not contacts.exists():
            return Response({
                'success': False,
                'message': 'No contacts found with the provided IDs',
                'updated_count': 0
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if all requested contacts were found
        found_ids = set(contacts.values_list('id', flat=True))
        requested_ids = set(contact_ids)
        missing_ids = requested_ids - found_ids

        if missing_ids:
            return Response({
                'success': False,
                'message': f'Some contacts not found: {list(missing_ids)}',
                'updated_count': 0
            }, status=status.HTTP_404_NOT_FOUND)

        # Apply updates
        updated_count = 0
        errors = []

        for contact in contacts:
            try:
                # Update each field
                for field, value in updates.items():
                    if field == 'tags' and isinstance(value, str):
                        # Handle comma-separated tags
                        value = [tag.strip() for tag in value.split(',') if tag.strip()]
                    setattr(contact, field, value)
                
                contact.save()
                updated_count += 1
            except Exception as e:
                errors.append(f"Contact {contact.id}: {str(e)}")

        response_data = {
            'success': True,
            'message': f'Successfully updated {updated_count} contacts',
            'updated_count': updated_count,
            'total_requested': len(contact_ids)
        }

        if errors:
            response_data['errors'] = errors
            response_data['message'] = f'Updated {updated_count} contacts with {len(errors)} errors'

        return Response(response_data, status=status.HTTP_200_OK)


class ContactBulkDeleteView(generics.GenericAPIView):
    """Bulk delete contacts."""

    permission_classes = [IsAuthenticated]
    serializer_class = ContactBulkDeleteSerializer

    def post(self, request, *args, **kwargs):
        """Bulk delete multiple contacts."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact_ids = serializer.validated_data['contact_ids']

        # Get contacts that belong to the user
        contacts = Contact.objects.filter(
            id__in=contact_ids,
            created_by=request.user,
            tenant=request.user.tenant
        )

        if not contacts.exists():
            return Response({
                'success': False,
                'message': 'No contacts found with the provided IDs',
                'deleted_count': 0
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if all requested contacts were found
        found_ids = set(contacts.values_list('id', flat=True))
        requested_ids = set(contact_ids)
        missing_ids = requested_ids - found_ids

        if missing_ids:
            return Response({
                'success': False,
                'message': f'Some contacts not found: {list(missing_ids)}',
                'deleted_count': 0
            }, status=status.HTTP_404_NOT_FOUND)

        # Delete contacts
        deleted_count, _ = contacts.delete()

        return Response({
            'success': True,
            'message': f'Successfully deleted {deleted_count} contacts',
            'deleted_count': deleted_count,
            'total_requested': len(contact_ids)
        }, status=status.HTTP_200_OK)


class SegmentListCreateView(generics.ListCreateAPIView):
    """List and create segments."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'contact_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SegmentCreateSerializer
        return SegmentSerializer

    def get_queryset(self):
        """Filter segments by user and tenant."""
        return get_tenant_queryset(Segment, self.request.user)


class SegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a segment."""

    permission_classes = [IsAuthenticated]
    serializer_class = SegmentSerializer

    def get_queryset(self):
        """Filter segments by user and tenant."""
        return get_tenant_queryset(Segment, self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def segment_update_count(request, segment_id):
    """Update segment contact count."""
    segment = get_object_or_404(
        Segment,
        id=segment_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    segment.update_contact_count()

    return Response({
        'message': 'Contact count updated',
        'contact_count': segment.contact_count
    })


class TemplateFilterSet(FilterSet):
    """Custom filter set for Template model."""
    
    class Meta:
        model = Template
        fields = ['category', 'language', 'channel', 'status', 'approved', 'is_favorite']
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class TemplateListCreateView(generics.ListCreateAPIView):
    """List and create templates with advanced filtering."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TemplateFilterSet
    search_fields = ['name', 'body_text', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at', 'usage_count', 'last_used_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TemplateCreateSerializer
        return TemplateListSerializer

    def get_queryset(self):
        """Filter templates by user and tenant with additional filtering."""
        queryset = get_tenant_queryset(Template, self.request.user)
        
        # Additional filtering based on query parameters
        favorites_only = self.request.query_params.get('favorites_only', '').lower() == 'true'
        approved_only = self.request.query_params.get('approved_only', '').lower() == 'true'
        
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        
        if approved_only:
            queryset = queryset.filter(approved=True)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Enhanced list view with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get filter options for frontend
        filter_options = {
            'categories': [{'value': choice[0], 'label': choice[1]} for choice in Template.CATEGORY_CHOICES],
            'languages': [{'value': choice[0], 'label': choice[1]} for choice in Template.LANGUAGE_CHOICES],
            'channels': [{'value': choice[0], 'label': choice[1]} for choice in Template.CHANNEL_CHOICES],
            'statuses': [{'value': choice[0], 'label': choice[1]} for choice in Template.STATUS_CHOICES],
        }
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'templates': serializer.data,
                'filter_options': filter_options,
                'total_count': queryset.count()
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'templates': serializer.data,
            'filter_options': filter_options,
            'total_count': queryset.count()
        })


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a template."""

    permission_classes = [IsAuthenticated]
    serializer_class = TemplateDetailSerializer

    def get_queryset(self):
        """Filter templates by user and tenant."""
        return get_tenant_queryset(Template, self.request.user)

    def get_serializer_class(self):
        """Use appropriate serializer based on method."""
        if self.request.method in ['PUT', 'PATCH']:
            return TemplateUpdateSerializer
        return TemplateDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Enhanced retrieve with additional data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add template statistics
        data = serializer.data
        data['statistics'] = {
            'total_uses': instance.usage_count,
            'last_used': instance.last_used_display,
            'created': instance.created_at.strftime('%Y-%m-%d'),
            'variables_count': len(instance.variables) if instance.variables else 0
        }
        
        return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def template_toggle_favorite(request, template_id):
    """Toggle favorite status of a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    template.toggle_favorite()
    
    return Response({
        'message': f'Template {"added to" if template.is_favorite else "removed from"} favorites',
        'is_favorite': template.is_favorite
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def template_increment_usage(request, template_id):
    """Increment usage count of a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    template.increment_usage()
    
    return Response({
        'message': 'Usage count updated',
        'usage_count': template.usage_count,
        'last_used_at': template.last_used_at.isoformat() if template.last_used_at else None
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def template_approve(request, template_id):
    """Approve a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    template.approved = True
    template.approval_status = 'approved'
    template.status = 'approved'
    template.save()
    
    return Response({
        'message': 'Template approved successfully',
        'approved': template.approved,
        'status': template.status
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def template_reject(request, template_id):
    """Reject a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    reason = request.data.get('reason', '')
    template.approved = False
    template.approval_status = 'rejected'
    template.status = 'rejected'
    template.save()
    
    return Response({
        'message': 'Template rejected successfully',
        'approved': template.approved,
        'status': template.status,
        'reason': reason
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_variables(request, template_id):
    """Get variables used in a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    variables = template.variables if template.variables else []
    
    return Response({
        'template_id': str(template.id),
        'template_name': template.name,
        'variables': variables,
        'variables_count': len(variables)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def template_copy(request, template_id):
    """Copy a template."""
    template = get_object_or_404(
        Template,
        id=template_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    
    new_name = request.data.get('name', f"{template.name} (Copy)")
    
    # Create new template
    new_template = Template.objects.create(
        name=new_name,
        category=template.category,
        language=template.language,
        channel=template.channel,
        body_text=template.body_text,
        description=template.description,
        created_by=request.user,
        tenant=request.user.tenant,
        status='draft'  # Start as draft
    )
    
    serializer = TemplateDetailSerializer(new_template)
    
    return Response({
        'message': 'Template copied successfully',
        'template': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_statistics(request):
    """Get template statistics for the user."""
    user = request.user
    
    # Validate user has a tenant
    try:
        validate_user_tenant(user)
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Template statistics
    total_templates = Template.objects.filter(
        created_by=user,
        tenant=user.tenant
    ).count()
    
    approved_templates = Template.objects.filter(
        created_by=user,
        tenant=user.tenant,
        approved=True
    ).count()
    
    draft_templates = Template.objects.filter(
        created_by=user,
        tenant=user.tenant,
        status='draft'
    ).count()
    
    favorite_templates = Template.objects.filter(
        created_by=user,
        tenant=user.tenant,
        is_favorite=True
    ).count()
    
    # Category breakdown
    category_stats = Template.objects.filter(
        created_by=user,
        tenant=user.tenant
    ).values('category').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Language breakdown
    language_stats = Template.objects.filter(
        created_by=user,
        tenant=user.tenant
    ).values('language').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Channel breakdown
    channel_stats = Template.objects.filter(
        created_by=user,
        tenant=user.tenant
    ).values('channel').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    return Response({
        'overview': {
            'total_templates': total_templates,
            'approved_templates': approved_templates,
            'draft_templates': draft_templates,
            'favorite_templates': favorite_templates,
            'approval_rate': (approved_templates / total_templates * 100) if total_templates > 0 else 0
        },
        'category_breakdown': [
            {
                'category': item['category'],
                'category_display': dict(Template.CATEGORY_CHOICES).get(item['category'], item['category']),
                'count': item['count']
            }
            for item in category_stats
        ],
        'language_breakdown': [
            {
                'language': item['language'],
                'language_display': dict(Template.LANGUAGE_CHOICES).get(item['language'], item['language']),
                'count': item['count']
            }
            for item in language_stats
        ],
        'channel_breakdown': [
            {
                'channel': item['channel'],
                'channel_display': dict(Template.CHANNEL_CHOICES).get(item['channel'], item['channel']),
                'count': item['count']
            }
            for item in channel_stats
        ]
    })


class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['contact__name', 'contact__phone_e164', 'subject']
    ordering_fields = ['created_at', 'last_message_at', 'unread_count']
    ordering = ['-last_message_at', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationSerializer
        return ConversationSerializer

    def get_queryset(self):
        """Filter conversations by user and tenant."""
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()

        if not hasattr(self.request.user, 'tenant') or not self.request.user.tenant:
            return Conversation.objects.none()

        return Conversation.objects.filter(
            contact__created_by=self.request.user,
            tenant=self.request.user.tenant
        ).select_related('contact')


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a conversation."""

    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        """Filter conversations by user and tenant."""
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()

        if not hasattr(self.request.user, 'tenant') or not self.request.user.tenant:
            return Conversation.objects.none()

        return Conversation.objects.filter(
            contact__created_by=self.request.user,
            tenant=self.request.user.tenant
        ).select_related('contact')


class MessageListCreateView(generics.ListCreateAPIView):
    """List and create messages."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['direction', 'provider', 'status', 'conversation']
    search_fields = ['text']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        """Filter messages by user and tenant."""
        if not self.request.user.is_authenticated:
            return Message.objects.none()

        if not hasattr(self.request.user, 'tenant') or not self.request.user.tenant:
            return Message.objects.none()

        return Message.objects.filter(
            conversation__contact__created_by=self.request.user,
            tenant=self.request.user.tenant
        ).select_related('conversation__contact')

    def perform_create(self, serializer):
        """Create message and trigger sending."""
        # Check rate limits BEFORE creating the message
        check_rate_limit(self.request, MESSAGE_RATE_LIMITER)

        # Create message
        message = serializer.save(tenant=self.request.user.tenant)

        # Queue message for sending
        send_message_task.delay(str(message.id))


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a message."""

    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Filter messages by user and tenant."""
        if not self.request.user.is_authenticated:
            return Message.objects.none()

        if not hasattr(self.request.user, 'tenant') or not self.request.user.tenant:
            return Message.objects.none()

        return Message.objects.filter(
            conversation__contact__created_by=self.request.user,
            tenant=self.request.user.tenant
        )


class CampaignListCreateView(generics.ListCreateAPIView):
    """List and create campaigns."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'template', 'segment']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'schedule_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampaignCreateSerializer
        return CampaignSerializer

    def get_queryset(self):
        """Filter campaigns by user and tenant."""
        if not self.request.user.is_authenticated:
            return Campaign.objects.none()

        if not hasattr(self.request.user, 'tenant') or not self.request.user.tenant:
            return Campaign.objects.none()

        return Campaign.objects.filter(
            created_by=self.request.user,
            tenant=self.request.user.tenant
        ).select_related('template', 'segment')


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a campaign."""

    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        """Filter campaigns by user and tenant."""
        return get_tenant_queryset(Campaign, self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_start(request, campaign_id):
    """Start a campaign."""
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        created_by=request.user,
        tenant=request.user.tenant
    )

    if campaign.status != 'draft':
        return Response({'error': 'Campaign can only be started from draft status'}, status=status.HTTP_400_BAD_REQUEST)

    campaign.start()

    # Queue campaign messages for sending
    from .tasks import send_campaign_messages_task
    send_campaign_messages_task.delay(str(campaign.id))

    return Response({'message': 'Campaign started successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_pause(request, campaign_id):
    """Pause a campaign."""
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    campaign.pause()

    return Response({'message': 'Campaign paused successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaign_cancel(request, campaign_id):
    """Cancel a campaign."""
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    campaign.cancel()

    return Response({'message': 'Campaign cancelled successfully'})


class FlowListCreateView(generics.ListCreateAPIView):
    """List and create flows."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'trigger_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FlowCreateSerializer
        return FlowSerializer

    def get_queryset(self):
        """Filter flows by user and tenant."""
        return get_tenant_queryset(Flow, self.request.user)


class FlowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a flow."""

    permission_classes = [IsAuthenticated]
    serializer_class = FlowSerializer

    def get_queryset(self):
        """Filter flows by user and tenant."""
        return get_tenant_queryset(Flow, self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flow_activate(request, flow_id):
    """Activate a flow."""
    flow = get_object_or_404(
        Flow,
        id=flow_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    flow.activate()

    return Response({'message': 'Flow activated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flow_deactivate(request, flow_id):
    """Deactivate a flow."""
    flow = get_object_or_404(
        Flow,
        id=flow_id,
        created_by=request.user,
        tenant=request.user.tenant
    )
    flow.deactivate()

    return Response({'message': 'Flow deactivated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_suggest_reply(request, conversation_id):
    """Get AI suggestions for a conversation."""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        contact__created_by=request.user,
        tenant=request.user.tenant
    )

    # Queue AI task
    ai_suggest_reply_task.delay(str(conversation.id))

    return Response({'message': 'AI suggestions requested'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_summarize_conversation(request, conversation_id):
    """Get AI summary for a conversation."""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        contact__created_by=request.user,
        tenant=request.user.tenant
    )

    # Queue AI task
    ai_summarize_conversation_task.delay(str(conversation.id))

    return Response({'message': 'AI summary requested'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """Get analytics overview for the user."""
    user = request.user

    # Validate user has a tenant
    try:
        validate_user_tenant(user)
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    # Message statistics
    total_messages = Message.objects.filter(
        conversation__contact__created_by=user,
        tenant=user.tenant
    ).count()
    sent_messages = Message.objects.filter(
        conversation__contact__created_by=user,
        tenant=user.tenant,
        direction='out',
        status__in=['sent', 'delivered', 'read']
    ).count()
    delivered_messages = Message.objects.filter(
        conversation__contact__created_by=user,
        tenant=user.tenant,
        direction='out',
        status__in=['delivered', 'read']
    ).count()
    read_messages = Message.objects.filter(
        conversation__contact__created_by=user,
        tenant=user.tenant,
        direction='out',
        status='read'
    ).count()

    # Conversation statistics
    total_conversations = Conversation.objects.filter(
        contact__created_by=user,
        tenant=user.tenant
    ).count()
    open_conversations = Conversation.objects.filter(
        contact__created_by=user,
        tenant=user.tenant,
        status='open'
    ).count()

    # Contact statistics
    total_contacts = Contact.objects.filter(
        created_by=user,
        tenant=user.tenant
    ).count()
    opted_in_contacts = Contact.objects.filter(
        created_by=user,
        tenant=user.tenant,
        opt_in_at__isnull=False,
        opt_out_at__isnull=True
    ).count()

    # Cost statistics
    total_cost = Message.objects.filter(
        conversation__contact__created_by=user,
        tenant=user.tenant
    ).aggregate(
        total=Sum('cost_micro')
    )['total'] or 0

    return Response({
        'messages': {
            'total': total_messages,
            'sent': sent_messages,
            'delivered': delivered_messages,
            'read': read_messages,
            'delivery_rate': (delivered_messages / sent_messages * 100) if sent_messages > 0 else 0,
            'read_rate': (read_messages / delivered_messages * 100) if delivered_messages > 0 else 0,
        },
        'conversations': {
            'total': total_conversations,
            'open': open_conversations,
        },
        'contacts': {
            'total': total_contacts,
            'opted_in': opted_in_contacts,
            'opt_in_rate': (opted_in_contacts / total_contacts * 100) if total_contacts > 0 else 0,
        },
        'cost': {
            'total_dollars': total_cost / 1000000,
            'total_micro': total_cost,
        }
    })


# =============================================
# PURCHASE HISTORY VIEWS
# =============================================

@swagger_auto_schema(
    method='get',
    operation_description="Get purchase history for the authenticated user with filtering and pagination support.",
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by purchase status",
            type=openapi.TYPE_STRING,
            enum=['pending', 'completed', 'failed', 'cancelled', 'refunded']
        ),
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Filter from date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="Filter to date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Items per page (max 100)",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description="Search in invoice number or package name",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "purchases": [
                            {
                                "id": "uuid",
                                "invoice_number": "INV-20240115-1234",
                                "package_name": "Standard Package",
                                "package_type": "standard",
                                "credits": 100,
                                "amount": 2250.00,
                                "unit_price": 22.50,
                                "payment_method": "mpesa",
                                "payment_method_display": "M-Pesa",
                                "payment_reference": "MP123456",
                                "status": "completed",
                                "status_display": "Completed",
                                "created_at": "2024-01-15T10:30:00Z",
                                "completed_at": "2024-01-15T10:31:00Z",
                                "updated_at": "2024-01-15T10:31:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 20,
                            "total_count": 25,
                            "total_pages": 2,
                            "has_next": True,
                            "has_previous": False,
                            "next_page": 2,
                            "previous_page": None
                        }
                    }
                }
            }
        ),
        401: openapi.Response(description="Unauthorized"),
        500: openapi.Response(description="Internal Server Error")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history(request):
    """
    Get purchase history for the authenticated user.
    GET /api/messaging/purchase-history/

    Query Parameters:
    - status: Filter by purchase status (pending, completed, failed, cancelled, refunded)
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - search: Search in invoice number or package name
    """
    try:
        from billing.models import Purchase
        from django.core.paginator import Paginator
        from django.db.models import Q, Count, Sum, Avg
        from datetime import datetime

        # Get query parameters with validation
        status_filter = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search', '').strip()

        # Validate page and page_size
        try:
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 items per page
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'message': 'Invalid page or page_size parameter'
            }, status=status.HTTP_400_BAD_REQUEST)

        if page < 1:
            return Response({
                'success': False,
                'message': 'Page number must be greater than 0'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Build queryset - filter by user
        queryset = Purchase.objects.filter(user=request.user).select_related('package')

        # Apply filters
        if status_filter:
            # Validate status filter
            valid_statuses = ['pending', 'completed', 'failed', 'cancelled', 'refunded']
            if status_filter not in valid_statuses:
                return Response({
                    'success': False,
                    'message': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(status=status_filter)

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)

        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(package__name__icontains=search)
            )

        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')

        # Pagination
        paginator = Paginator(queryset, page_size)
        total_count = paginator.count

        try:
            purchases_page = paginator.page(page)
        except:
            return Response({
                'success': False,
                'message': f'Invalid page number. Available pages: 1-{paginator.num_pages}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Serialize purchase data
        purchase_data = []
        for purchase in purchases_page:
            purchase_data.append({
                'id': str(purchase.id),
                'invoice_number': purchase.invoice_number,
                'package_name': purchase.package.name,
                'package_type': purchase.package.package_type,
                'credits': purchase.credits,
                'amount': float(purchase.amount),
                'unit_price': float(purchase.unit_price),
                'payment_method': purchase.payment_method,
                'payment_method_display': purchase.get_payment_method_display(),
                'payment_reference': purchase.payment_reference,
                'status': purchase.status,
                'status_display': purchase.get_status_display(),
                'created_at': purchase.created_at.isoformat(),
                'completed_at': purchase.completed_at.isoformat() if purchase.completed_at else None,
                'updated_at': purchase.updated_at.isoformat()
            })

        return Response({
            'success': True,
            'data': {
                'purchases': purchase_data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': paginator.num_pages,
                    'has_next': purchases_page.has_next(),
                    'has_previous': purchases_page.has_previous(),
                    'next_page': purchases_page.next_page_number() if purchases_page.has_next() else None,
                    'previous_page': purchases_page.previous_page_number() if purchases_page.has_previous() else None
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase history',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Get purchase history summary statistics for the authenticated user.",
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Filter from date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="Filter to date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "total_purchases": 25,
                        "total_amount": 125000.00,
                        "total_credits": 5000,
                        "completed_purchases": 20,
                        "pending_purchases": 3,
                        "failed_purchases": 2,
                        "cancelled_purchases": 0,
                        "refunded_purchases": 0,
                        "average_purchase_amount": 5000.00,
                        "last_purchase_date": "2024-01-15T10:30:00Z"
                    }
                }
            }
        ),
        401: openapi.Response(description="Unauthorized"),
        500: openapi.Response(description="Internal Server Error")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history_summary(request):
    """
    Get purchase history summary statistics for the authenticated user.
    GET /api/messaging/purchase-history/summary/

    Query Parameters:
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    """
    try:
        from billing.models import Purchase
        from django.db.models import Count, Sum, Avg, Max
        from datetime import datetime

        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Build queryset - filter by user
        queryset = Purchase.objects.filter(user=request.user)

        # Apply date filters
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate statistics
        stats = queryset.aggregate(
            total_purchases=Count('id'),
            total_amount=Sum('amount'),
            total_credits=Sum('credits'),
            average_purchase_amount=Avg('amount'),
            last_purchase_date=Max('created_at')
        )

        # Count by status
        status_counts = queryset.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}

        summary_data = {
            'total_purchases': stats['total_purchases'] or 0,
            'total_amount': float(stats['total_amount'] or 0),
            'total_credits': stats['total_credits'] or 0,
            'completed_purchases': status_dict.get('completed', 0),
            'pending_purchases': status_dict.get('pending', 0),
            'failed_purchases': status_dict.get('failed', 0),
            'cancelled_purchases': status_dict.get('cancelled', 0),
            'refunded_purchases': status_dict.get('refunded', 0),
            'average_purchase_amount': float(stats['average_purchase_amount'] or 0),
            'last_purchase_date': stats['last_purchase_date'].isoformat() if stats['last_purchase_date'] else None
        }

        return Response({
            'success': True,
            'data': summary_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase history summary',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Get detailed information about a specific purchase.",
    manual_parameters=[
        openapi.Parameter(
            'purchase_id',
            openapi.IN_PATH,
            description="Purchase UUID",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "id": "uuid",
                        "invoice_number": "INV-20240115-1234",
                        "package": {
                            "id": "uuid",
                            "name": "Standard Package",
                            "package_type": "standard",
                            "credits": 100,
                            "price": 2250.00,
                            "unit_price": 22.50,
                            "features": ["SMS + WhatsApp", "Priority Support"],
                            "is_popular": True
                        },
                        "credits": 100,
                        "amount": 2250.00,
                        "unit_price": 22.50,
                        "payment_method": "mpesa",
                        "payment_method_display": "M-Pesa",
                        "payment_reference": "MP123456",
                        "status": "completed",
                        "status_display": "Completed",
                        "created_at": "2024-01-15T10:30:00Z",
                        "completed_at": "2024-01-15T10:31:00Z",
                        "updated_at": "2024-01-15T10:31:00Z"
                    }
                }
            }
        ),
        401: openapi.Response(description="Unauthorized"),
        404: openapi.Response(description="Purchase not found"),
        500: openapi.Response(description="Internal Server Error")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_detail(request, purchase_id):
    """
    Get detailed information about a specific purchase.
    GET /api/messaging/purchase-history/{purchase_id}/
    """
    try:
        from billing.models import Purchase
        from django.shortcuts import get_object_or_404

        # Get purchase (filter by user for security)
        purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)

        # Serialize purchase data
        purchase_data = {
            'id': str(purchase.id),
            'invoice_number': purchase.invoice_number,
            'package': {
                'id': str(purchase.package.id),
                'name': purchase.package.name,
                'package_type': purchase.package.package_type,
                'credits': purchase.package.credits,
                'price': float(purchase.package.price),
                'unit_price': float(purchase.package.unit_price),
                'features': purchase.package.features,
                'is_popular': purchase.package.is_popular
            },
            'credits': purchase.credits,
            'amount': float(purchase.amount),
            'unit_price': float(purchase.unit_price),
            'payment_method': purchase.payment_method,
            'payment_method_display': purchase.get_payment_method_display(),
            'payment_reference': purchase.payment_reference,
            'status': purchase.status,
            'status_display': purchase.get_status_display(),
            'created_at': purchase.created_at.isoformat(),
            'completed_at': purchase.completed_at.isoformat() if purchase.completed_at else None,
            'updated_at': purchase.updated_at.isoformat()
        }

        return Response({
            'success': True,
            'data': purchase_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve purchase details',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Sender ID Management Views (for frontend compatibility)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sender_ids_list(request):
    """Get list of sender IDs for the current tenant."""
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        sender_ids = SMSSenderID.objects.filter(
            tenant=tenant,
            status='active'
        ).order_by('-created_at')

        data = []
        for sender_id in sender_ids:
            data.append({
                'id': str(sender_id.id),
                'sender_id': sender_id.sender_id,
                'sample_content': sender_id.sample_content,
                'status': sender_id.status,
                'created_at': sender_id.created_at.isoformat(),
                'updated_at': sender_id.updated_at.isoformat()
            })

        return Response({
            'success': True,
            'data': data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve sender IDs',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_sender_id(request):
    """Request a new sender ID."""
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Redirect to the sender requests endpoint
        return Response({
            'success': True,
            'message': 'Please use /api/messaging/sender-requests/ endpoint for sender ID requests',
            'redirect_url': '/api/messaging/sender-requests/'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to request sender ID',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sender_id_detail(request, pk):
    """Get details of a specific sender ID."""
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        sender_id = get_object_or_404(
            SMSSenderID,
            id=pk,
            tenant=tenant
        )

        data = {
            'id': str(sender_id.id),
            'sender_id': sender_id.sender_id,
            'sample_content': sender_id.sample_content,
            'status': sender_id.status,
            'provider': sender_id.provider.name if sender_id.provider else None,
            'created_at': sender_id.created_at.isoformat(),
            'updated_at': sender_id.updated_at.isoformat()
        }

        return Response({
            'success': True,
            'data': data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve sender ID details',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sender_id_status(request, pk):
    """Get status of a specific sender ID."""
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        sender_id = get_object_or_404(
            SMSSenderID,
            id=pk,
            tenant=tenant
        )

        data = {
            'id': str(sender_id.id),
            'sender_id': sender_id.sender_id,
            'status': sender_id.status,
            'is_active': sender_id.status == 'active'
        }

        return Response({
            'success': True,
            'data': data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to retrieve sender ID status',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
