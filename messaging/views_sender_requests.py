"""
Views for sender name request functionality.
Handles form submission, file uploads, and admin management.
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models_sms import SenderNameRequest
from .serializers_sms import (
    SenderNameRequestSerializer,
    SenderNameRequestCreateSerializer,
    SenderNameRequestUpdateSerializer
)
from core.permissions import IsTenantMember


class SenderNameRequestPagination(PageNumberPagination):
    """Custom pagination for sender name requests."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SenderNameRequestListCreateView(ListCreateAPIView):
    """
    List and create sender name requests.
    """
    serializer_class = SenderNameRequestSerializer
    pagination_class = SenderNameRequestPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['sender_name', 'use_case']
    ordering_fields = ['created_at', 'updated_at', 'sender_name']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter requests by tenant."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return SenderNameRequest.objects.none()

        # Users can only see their own requests unless they're admin
        if self.request.user.is_staff:
            return SenderNameRequest.objects.filter(tenant=tenant)
        else:
            return SenderNameRequest.objects.filter(
                tenant=tenant,
                created_by=self.request.user
            )

    def perform_create(self, serializer):
        """Set tenant and user when creating request."""
        tenant = getattr(self.request, 'tenant', None)
        serializer.save(tenant=tenant, created_by=self.request.user)


class SenderNameRequestDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a sender name request.
    """
    serializer_class = SenderNameRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter requests by tenant."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return SenderNameRequest.objects.none()

        # Users can only see their own requests unless they're admin
        if self.request.user.is_staff:
            return SenderNameRequest.objects.filter(tenant=tenant)
        else:
            return SenderNameRequest.objects.filter(
                tenant=tenant,
                created_by=self.request.user
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_sender_name_request(request):
    """
    Submit a new sender name request with file uploads.

    POST /api/messaging/sender-requests/submit/

    Request Body (multipart/form-data):
    {
        "sender_name": "MYCOMPANY",
        "use_case": "We will use this sender name for customer notifications...",
        "supporting_documents": [file1, file2, ...] // optional
    }

    Response:
    {
        "success": true,
        "message": "Sender name request submitted successfully",
        "data": {
            "created_request": {
                "id": "uuid",
                "sender_name": "MYCOMPANY",
                "status": "pending",
                "created_at": "2024-01-01T10:00:00Z",
                ...
            },
            "user_requests": [
                {
                    "id": "uuid",
                    "sender_name": "MYCOMPANY",
                    "status": "pending",
                    "created_at": "2024-01-01T10:00:00Z",
                    ...
                },
                ...
            ],
            "user_stats": {
                "total_requests": 3,
                "pending_requests": 2,
                "approved_requests": 1,
                "rejected_requests": 0,
                "requires_changes_requests": 0
            },
            "total_count": 3
        }
    }
    """
    try:
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate form data
        serializer = SenderNameRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sender_name = data['sender_name']
        use_case = data['use_case']
        supporting_documents = data.get('supporting_documents', [])

        # Check if request already exists
        existing_request = SenderNameRequest.objects.filter(
            tenant=tenant,
            sender_name=sender_name
        ).first()

        if existing_request:
            return Response({
                'success': False,
                'message': f'A request for sender name "{sender_name}" already exists',
                'existing_request_id': str(existing_request.id)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Handle file uploads
        uploaded_files = []
        if supporting_documents:
            for file in supporting_documents:
                # Generate unique filename
                file_ext = os.path.splitext(file.name)[1]
                unique_filename = f"sender_requests/{uuid.uuid4()}{file_ext}"

                # Save file
                file_path = default_storage.save(unique_filename, file)
                uploaded_files.append(file_path)

        # Create sender name request
        sender_request = SenderNameRequest.objects.create(
            tenant=tenant,
            sender_name=sender_name,
            use_case=use_case,
            supporting_documents=uploaded_files,
            created_by=request.user
        )

        # Get user's updated list and stats
        user_requests = SenderNameRequest.objects.filter(
            tenant=tenant,
            created_by=request.user
        ).order_by('-created_at')

        # Serialize the created request
        created_request_serializer = SenderNameRequestSerializer(sender_request)

        # Serialize user's complete list
        user_requests_serializer = SenderNameRequestSerializer(user_requests, many=True)

        # Calculate user's statistics
        user_stats = {
            'total_requests': user_requests.count(),
            'pending_requests': user_requests.filter(status='pending').count(),
            'approved_requests': user_requests.filter(status='approved').count(),
            'rejected_requests': user_requests.filter(status='rejected').count(),
            'requires_changes_requests': user_requests.filter(status='requires_changes').count(),
        }

        # Return response with created request, updated list, and stats
        return Response({
            'success': True,
            'message': 'Sender name request submitted successfully',
            'data': {
                'created_request': created_request_serializer.data,
                'user_requests': user_requests_serializer.data,
                'user_stats': user_stats,
                'total_count': user_requests.count()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error submitting request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sender_name_requests(request):
    """
    Get list of sender name requests for the current tenant.

    GET /api/messaging/sender-requests/

    Query Parameters:
    - status: Filter by status (pending, approved, rejected, requires_changes)
    - search: Search in sender_name and use_case
    - page: Page number for pagination
    - page_size: Number of items per page

    Response:
    {
        "success": true,
        "data": {
            "results": [...],
            "count": 10,
            "next": "http://...",
            "previous": null
        }
    }
    """
    try:
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get queryset
        queryset = SenderNameRequest.objects.filter(tenant=tenant)

        # Filter by user if not admin
        if not request.user.is_staff:
            queryset = queryset.filter(created_by=request.user)

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                sender_name__icontains=search_query
            ) | queryset.filter(
                use_case__icontains=search_query
            )

        # Order by creation date
        queryset = queryset.order_by('-created_at')

        # Pagination
        paginator = SenderNameRequestPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = SenderNameRequestSerializer(page, many=True)
            paginated_data = paginator.get_paginated_response(serializer.data).data
            return Response({
                'success': True,
                'data': paginated_data
            })

        # No pagination
        serializer = SenderNameRequestSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': queryset.count()
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching requests: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sender_name_request(request, request_id):
    """
    Get details of a specific sender name request.

    GET /api/messaging/sender-requests/{request_id}/

    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "sender_name": "MYCOMPANY",
            "status": "pending",
            ...
        }
    }
    """
    try:
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get request
        try:
            sender_request = SenderNameRequest.objects.get(
                id=request_id,
                tenant=tenant
            )
        except SenderNameRequest.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sender name request not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions
        if not request.user.is_staff and sender_request.created_by != request.user:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this request'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = SenderNameRequestSerializer(sender_request)
        return Response({
            'success': True,
            'data': serializer.data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_sender_name_request(request, request_id):
    """
    Update a sender name request (admin only).

    PUT /api/messaging/sender-requests/{request_id}/update/

    Request Body:
    {
        "status": "approved",
        "admin_notes": "Request approved after review"
    }

    Response:
    {
        "success": true,
        "message": "Request updated successfully",
        "data": {...}
    }
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Only administrators can update requests'
            }, status=status.HTTP_403_FORBIDDEN)

        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get request
        try:
            sender_request = SenderNameRequest.objects.get(
                id=request_id,
                tenant=tenant
            )
        except SenderNameRequest.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sender name request not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate update data
        serializer = SenderNameRequestUpdateSerializer(
            sender_request,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update request
        serializer.save(
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )

        # Return updated data
        response_serializer = SenderNameRequestSerializer(sender_request)
        return Response({
            'success': True,
            'message': 'Request updated successfully',
            'data': response_serializer.data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error updating request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_sender_name_request(request, request_id):
    """
    Delete a sender name request.

    DELETE /api/messaging/sender-requests/{request_id}/

    Response:
    {
        "success": true,
        "message": "Request deleted successfully"
    }
    """
    try:
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get request
        try:
            sender_request = SenderNameRequest.objects.get(
                id=request_id,
                tenant=tenant
            )
        except SenderNameRequest.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sender name request not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions
        if not request.user.is_staff and sender_request.created_by != request.user:
            return Response({
                'success': False,
                'message': 'You do not have permission to delete this request'
            }, status=status.HTTP_403_FORBIDDEN)

        # Delete supporting documents
        for file_path in sender_request.supporting_documents:
            try:
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
            except Exception as e:
                # Log error but continue with deletion
                print(f"Error deleting file {file_path}: {str(e)}")

        # Delete request
        sender_request.delete()

        return Response({
            'success': True,
            'message': 'Request deleted successfully'
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error deleting request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sender_name_request_stats(request):
    """
    Get statistics for sender name requests created by the current user.

    GET /api/messaging/sender-requests/stats/

    Response:
    {
        "success": true,
        "data": {
            "total_requests": 4,
            "pending_requests": 2,
            "approved_requests": 1,
            "rejected_requests": 1,
            "requires_changes_requests": 0
        }
    }
    """
    try:
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user's requests only (like campaigns)
        user_requests = SenderNameRequest.objects.filter(
            tenant=tenant,
            created_by=request.user
        )

        stats = {
            'total_requests': user_requests.count(),
            'pending_requests': user_requests.filter(status='pending').count(),
            'approved_requests': user_requests.filter(status='approved').count(),
            'rejected_requests': user_requests.filter(status='rejected').count(),
            'requires_changes_requests': user_requests.filter(status='requires_changes').count(),
        }

        return Response({
            'success': True,
            'data': stats
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_sender_requests_dashboard(request):
    """
    Admin dashboard for sender name requests management.

    GET /api/messaging/sender-requests/admin/dashboard/

    Returns comprehensive statistics and recent requests for admin dashboard.
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all requests for the tenant
        all_requests = SenderNameRequest.objects.filter(tenant=tenant)

        # Calculate statistics
        stats = {
            'total_requests': all_requests.count(),
            'pending_requests': all_requests.filter(status='pending').count(),
            'approved_requests': all_requests.filter(status='approved').count(),
            'rejected_requests': all_requests.filter(status='rejected').count(),
            'requires_changes_requests': all_requests.filter(status='requires_changes').count(),
        }

        # Recent requests (last 10)
        recent_requests = all_requests.order_by('-created_at')[:10]
        recent_requests_data = SenderNameRequestSerializer(recent_requests, many=True).data

        # Pending requests that need attention
        pending_requests = all_requests.filter(status='pending').order_by('created_at')
        pending_requests_data = SenderNameRequestSerializer(pending_requests, many=True).data

        return Response({
            'success': True,
            'data': {
                'stats': stats,
                'recent_requests': recent_requests_data,
                'pending_requests': pending_requests_data,
                'tenant_name': tenant.name,
                'admin_user': request.user.email
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching dashboard data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
