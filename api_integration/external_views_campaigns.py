"""
External Campaigns API views for integrations.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .utils import format_api_response


@api_view(['GET'])
def list_campaigns(request):
    """List campaigns."""
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
    
    # For now, return empty list as campaigns are not implemented yet
    return Response(format_api_response(
        success=True,
        data={
            'campaigns': [],
            'total': 0
        },
        message="Campaigns retrieved successfully"
    ))


@api_view(['POST'])
def create_campaign(request):
    """Create a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
def get_campaign(request, campaign_id):
    """Get a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['PUT'])
def update_campaign(request, campaign_id):
    """Update a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['DELETE'])
def delete_campaign(request, campaign_id):
    """Delete a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
def start_campaign(request, campaign_id):
    """Start a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
def stop_campaign(request, campaign_id):
    """Stop a campaign."""
    return Response(format_api_response(
        success=False,
        message="Campaigns feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)

