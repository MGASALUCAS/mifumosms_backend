"""
Enhanced serializers for team management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Membership

User = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model with enhanced fields."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_first_name', 'user_last_name',
            'user_avatar', 'role', 'role_display', 'status', 'status_display',
            'invited_by', 'invited_by_email', 'invited_by_name', 
            'invited_at', 'joined_at', 'invitation_token'
        ]
        read_only_fields = ['id', 'invited_at', 'joined_at', 'invitation_token']


class MembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new memberships."""
    
    email = serializers.EmailField(write_only=True)
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES, default='agent')
    
    class Meta:
        model = Membership
        fields = ['email', 'role']
    
    def validate_role(self, value):
        """Validate role assignment."""
        request = self.context.get('request')
        tenant = self.context.get('tenant')
        
        if not request or not tenant:
            return value
        
        # Only owners can assign owner role
        if value == 'owner':
            user_membership = Membership.objects.filter(
                user=request.user,
                tenant=tenant,
                role='owner',
                status='active'
            ).first()
            
            if not user_membership:
                raise serializers.ValidationError(
                    'Only owners can assign owner role'
                )
        
        return value
    
    def create(self, validated_data):
        """Create membership by email."""
        email = validated_data.pop('email')
        tenant = self.context['tenant']
        invited_by = self.context['request'].user
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create user if doesn't exist
            user = User.objects.create_user(
                email=email,
                first_name='',
                last_name=''
            )
        
        # Check if user is already a member
        if Membership.objects.filter(tenant=tenant, user=user).exists():
            raise serializers.ValidationError(
                'User is already a member of this tenant'
            )
        
        membership = Membership.objects.create(
            tenant=tenant,
            user=user,
            invited_by=invited_by,
            **validated_data
        )
        
        return membership


class MembershipUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating memberships."""
    
    class Meta:
        model = Membership
        fields = ['role', 'status']
    
    def validate_role(self, value):
        """Validate role changes."""
        request = self.context.get('request')
        tenant = self.context.get('tenant')
        
        if not request or not tenant:
            return value
        
        # Only owners can assign owner role
        if value == 'owner':
            user_membership = Membership.objects.filter(
                user=request.user,
                tenant=tenant,
                role='owner',
                status='active'
            ).first()
            
            if not user_membership:
                raise serializers.ValidationError(
                    'Only owners can assign owner role'
                )
        
        return value
    
    def validate_status(self, value):
        """Validate status changes."""
        instance = self.instance
        
        # Prevent changing owner status to suspended
        if instance and instance.role == 'owner' and value == 'suspended':
            raise serializers.ValidationError(
                'Cannot suspend owners'
            )
        
        return value


class TeamStatsSerializer(serializers.Serializer):
    """Serializer for team statistics."""
    
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    pending_members = serializers.IntegerField()
    suspended_members = serializers.IntegerField()
    owners = serializers.IntegerField()
    admins = serializers.IntegerField()
    agents = serializers.IntegerField()


class InvitationAcceptSerializer(serializers.Serializer):
    """Serializer for accepting invitations."""
    
    token = serializers.CharField(max_length=32)


class InvitationRejectSerializer(serializers.Serializer):
    """Serializer for rejecting invitations."""
    
    token = serializers.CharField(max_length=32)
