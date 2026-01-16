"""
User views
"""
from rest_framework import generics, permissions, status, viewsets, mixins, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    WarningSerializer, BanSerializer, ModerationActionSerializer
)
from .models import Warning, Ban, ModerationAction
from .permissions import IsModerator, IsModeratorOrReadOnly

User = get_user_model()


def get_client_ip(request):
    """
    Get client IP address, accounting for proxies
    
    Note: X-Forwarded-For can be spoofed. In production, ensure requests
    come through trusted proxies and consider additional validation.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class UserRegistrationView(generics.CreateAPIView):
    """Register a new user"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """Get public user profile"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics"""
    user = request.user
    from apps.schematics.models import Schematic

    total_schematics = Schematic.objects.filter(owner=user).count()
    public_schematics = Schematic.objects.filter(owner=user, is_public=True).count()

    return Response({
        'total_schematics': total_schematics,
        'public_schematics': public_schematics,
        'storage_used': user.storage_used,
        'storage_quota': user.storage_quota,
        'storage_available': user.storage_available,
        'storage_percentage': user.storage_percentage,
    })


class WarningViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """ViewSet for managing user warnings (create and read only)"""
    serializer_class = WarningSerializer
    permission_classes = [IsModeratorOrReadOnly]
    
    def get_queryset(self):
        """Filter warnings based on user role"""
        user = self.request.user
        if user.is_staff:
            # Moderators can see all warnings
            return Warning.objects.all()
        # Regular users can only see their own warnings
        return Warning.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Create warning and log the action"""
        target_user = serializer.validated_data['user']
        
        # Prevent self-warning
        if target_user == self.request.user:
            raise serializers.ValidationError(
                {'user': 'You cannot issue a warning to yourself'}
            )
        
        with transaction.atomic():
            warning = serializer.save(issued_by=self.request.user)
            # Log the moderation action
            ModerationAction.objects.create(
                user=warning.user,
                moderator=self.request.user,
                action_type='warning',
                reason=warning.reason,
                ip_address=get_client_ip(self.request)
            )


class BanViewSet(mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """ViewSet for managing user bans (create and read only)"""
    serializer_class = BanSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        """Return all bans for moderators"""
        return Ban.objects.all()
    
    def perform_create(self, serializer):
        """Create ban and log the action"""
        target_user = serializer.validated_data['user']
        
        # Prevent self-banning
        if target_user == self.request.user:
            raise serializers.ValidationError(
                {'user': 'You cannot ban yourself'}
            )
        
        # Prevent non-superusers from banning staff members
        if target_user.is_staff and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                {'user': 'Only superusers can ban staff members'}
            )
        
        with transaction.atomic():
            ban = serializer.save(issued_by=self.request.user)
            # Log the moderation action
            ModerationAction.objects.create(
                user=ban.user,
                moderator=self.request.user,
                action_type='ban',
                reason=ban.reason,
                details={
                    'ban_type': ban.ban_type,
                    'expires_at': ban.expires_at.isoformat() if ban.expires_at else None
                },
                ip_address=get_client_ip(self.request)
            )
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a ban"""
        ban = self.get_object()
        if not ban.is_active:
            return Response(
                {'error': 'Ban is already inactive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            ban.is_active = False
            ban.save()
            
            # Unban the user
            ban.user.unban()
            
            # Log the moderation action
            ModerationAction.objects.create(
                user=ban.user,
                moderator=request.user,
                action_type='unban',
                reason=f"Ban #{ban.id} revoked",
                ip_address=get_client_ip(request)
            )
        
        return Response({'status': 'Ban revoked successfully'})


class ModerationActionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing moderation action audit log"""
    serializer_class = ModerationActionSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        """Return all moderation actions for moderators"""
        return ModerationAction.objects.all()


@api_view(['POST'])
@permission_classes([IsModerator])
def disable_user_account(request, username):
    """Disable a user account (soft deactivation)"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is already disabled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prevent self-disabling
    if user == request.user:
        return Response(
            {'error': 'You cannot disable your own account'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prevent non-superusers from disabling staff members
    if user.is_staff and not request.user.is_superuser:
        return Response(
            {'error': 'Only superusers can disable staff members'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    reason = request.data.get('reason', 'No reason provided')
    
    with transaction.atomic():
        user.is_active = False
        user.save()
        
        # Log the moderation action
        ModerationAction.objects.create(
            user=user,
            moderator=request.user,
            action_type='disable',
            reason=reason,
            ip_address=get_client_ip(request)
        )
    
    return Response({
        'status': 'User account disabled successfully',
        'username': username
    })


@api_view(['POST'])
@permission_classes([IsModerator])
def enable_user_account(request, username):
    """Enable a user account"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if user.is_active:
        return Response(
            {'error': 'User account is already enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', 'No reason provided')
    
    with transaction.atomic():
        # Only clear ban information if the user has an active temporary ban
        if user.ban_expires_at and user.ban_expires_at > timezone.now():
            user.ban_expires_at = None
            user.ban_reason = ''
        user.is_active = True
        user.save()
        
        # Log the moderation action
        ModerationAction.objects.create(
            user=user,
            moderator=request.user,
            action_type='enable',
            reason=reason,
            ip_address=get_client_ip(request)
        )
    
    return Response({
        'status': 'User account enabled successfully',
        'username': username
    })
