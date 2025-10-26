"""
External Contacts API views for integrations.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .utils import format_api_response
from messaging.models import Contact, Segment


@api_view(['GET'])
def list_contacts(request):
    """List contacts."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        search = request.GET.get('search')
        segment_id = request.GET.get('segment_id')
        
        # Build query
        contacts = Contact.objects.filter(tenant=account.tenant)
        
        if search:
            contacts = contacts.filter(
                Q(name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
        
        if segment_id:
            contacts = contacts.filter(segments__id=segment_id)
        
        # Apply pagination
        total = contacts.count()
        contacts = contacts.order_by('-created_at')[offset:offset + limit]
        
        # Format response
        contact_list = []
        for contact in contacts:
            contact_list.append({
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat()
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'contacts': contact_list,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total
                }
            },
            message="Contacts retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_contact(request):
    """Create a new contact."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    required_fields = ['name', 'phone_number']
    for field in required_fields:
        if field not in request.data:
            return Response(format_api_response(
                success=False,
                message=f"Missing required field: {field}"
            ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create contact
        contact = Contact.objects.create(
            tenant=account.tenant,
            name=request.data['name'],
            phone_number=request.data['phone_number'],
            email=request.data.get('email', ''),
            tags=request.data.get('tags', []),
            is_active=request.data.get('is_active', True),
            created_by=account.owner
        )
        
        return Response(format_api_response(
            success=True,
            data={
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat()
            },
            message="Contact created successfully"
        ), status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_contact(request, contact_id):
    """Get a specific contact."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get contact
        contact = get_object_or_404(
            Contact,
            pk=contact_id,
            tenant=account.tenant
        )
        
        return Response(format_api_response(
            success=True,
            data={
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat()
            },
            message="Contact retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_contact(request, contact_id):
    """Update a contact."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get contact
        contact = get_object_or_404(
            Contact,
            pk=contact_id,
            tenant=account.tenant
        )
        
        # Update fields
        if 'name' in request.data:
            contact.name = request.data['name']
        if 'phone_number' in request.data:
            contact.phone_number = request.data['phone_number']
        if 'email' in request.data:
            contact.email = request.data['email']
        if 'tags' in request.data:
            contact.tags = request.data['tags']
        if 'is_active' in request.data:
            contact.is_active = request.data['is_active']
        
        contact.save()
        
        return Response(format_api_response(
            success=True,
            data={
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active,
                'updated_at': contact.updated_at.isoformat()
            },
            message="Contact updated successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_contact(request, contact_id):
    """Delete a contact."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get contact
        contact = get_object_or_404(
            Contact,
            pk=contact_id,
            tenant=account.tenant
        )
        
        contact.delete()
        
        return Response(format_api_response(
            success=True,
            message="Contact deleted successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_contacts(request):
    """Search contacts."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # Validate request data
    if 'q' not in request.GET:
        return Response(format_api_response(
            success=False,
            message="Missing required parameter: q"
        ), status=status.HTTP_400_BAD_REQUEST)
    
    try:
        search_query = request.GET['q']
        limit = int(request.GET.get('limit', 20))
        
        # Search contacts
        contacts = Contact.objects.filter(
            tenant=account.tenant
        ).filter(
            Q(name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )[:limit]
        
        # Format response
        contact_list = []
        for contact in contacts:
            contact_list.append({
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'contacts': contact_list,
                'query': search_query,
                'count': len(contact_list)
            },
            message="Contact search completed successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_contact_by_phone(request, phone):
    """Get contact by phone number."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get contact by phone
        contact = Contact.objects.filter(
            tenant=account.tenant,
            phone_number__icontains=phone
        ).first()
        
        if not contact:
            return Response(format_api_response(
                success=False,
                message="Contact not found",
                error_code="CONTACT_NOT_FOUND"
            ), status=status.HTTP_404_NOT_FOUND)
        
        return Response(format_api_response(
            success=True,
            data={
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat()
            },
            message="Contact retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_segments(request):
    """List contact segments."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get segments
        segments = Segment.objects.filter(tenant=account.tenant).order_by('name')
        
        # Format response
        segment_list = []
        for segment in segments:
            segment_list.append({
                'segment_id': str(segment.id),
                'name': segment.name,
                'description': segment.description,
                'contact_count': segment.contacts.count(),
                'created_at': segment.created_at.isoformat()
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'segments': segment_list
            },
            message="Segments retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_segment_contacts(request, segment_id):
    """Get contacts in a segment."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        # Get segment
        segment = get_object_or_404(
            Segment,
            pk=segment_id,
            tenant=account.tenant
        )
        
        # Get contacts in segment
        contacts = segment.contacts.all()
        
        # Format response
        contact_list = []
        for contact in contacts:
            contact_list.append({
                'contact_id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'email': contact.email,
                'tags': contact.tags,
                'is_active': contact.is_active
            })
        
        return Response(format_api_response(
            success=True,
            data={
                'segment_id': str(segment.id),
                'segment_name': segment.name,
                'contacts': contact_list,
                'count': len(contact_list)
            },
            message="Segment contacts retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_segment(request):
    """Create a segment."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        criteria = request.data.get('criteria', {})
        
        if not name:
            return Response(format_api_response(
                success=False,
                message="Segment name is required"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        # Create segment
        segment = Segment.objects.create(
            name=name,
            description=description,
            criteria=criteria,
            tenant=account.tenant,
            created_by=account.owner
        )
        
        return Response(format_api_response(
            success=True,
            data={
                'segment_id': str(segment.id),
                'name': segment.name,
                'description': segment.description,
                'criteria': segment.criteria,
                'created_at': segment.created_at.isoformat()
            },
            message="Segment created successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_segment(request, segment_id):
    """Get a segment."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        segment = get_object_or_404(
            Segment,
            pk=segment_id,
            tenant=account.tenant
        )
        
        return Response(format_api_response(
            success=True,
            data={
                'segment_id': str(segment.id),
                'name': segment.name,
                'description': segment.description,
                'criteria': segment.criteria,
                'contact_count': segment.contacts.count(),
                'created_at': segment.created_at.isoformat(),
                'updated_at': segment.updated_at.isoformat()
            },
            message="Segment retrieved successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_segment(request, segment_id):
    """Update a segment."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        segment = get_object_or_404(
            Segment,
            pk=segment_id,
            tenant=account.tenant
        )
        
        # Update fields
        if 'name' in request.data:
            segment.name = request.data['name'].strip()
        if 'description' in request.data:
            segment.description = request.data['description'].strip()
        if 'criteria' in request.data:
            segment.criteria = request.data['criteria']
        
        segment.save()
        
        return Response(format_api_response(
            success=True,
            data={
                'segment_id': str(segment.id),
                'name': segment.name,
                'description': segment.description,
                'criteria': segment.criteria,
                'updated_at': segment.updated_at.isoformat()
            },
            message="Segment updated successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_segment(request, segment_id):
    """Delete a segment."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    try:
        segment = get_object_or_404(
            Segment,
            pk=segment_id,
            tenant=account.tenant
        )
        
        segment.delete()
        
        return Response(format_api_response(
            success=True,
            message="Segment deleted successfully"
        ))
        
    except Exception as e:
        return Response(format_api_response(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(e)
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
