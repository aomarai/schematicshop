"""
User views
"""
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    WarningSerializer, BanSerializer, ModerationActionSerializer
)
from .models import Warning, Ban, ModerationAction
from .permissions import IsModerator, IsModeratorOrReadOnly

User = get_user_model()


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


class WarningViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user warnings"""
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
        warning = serializer.save(issued_by=self.request.user)
        # Log the moderation action
        ModerationAction.objects.create(
            user=warning.user,
            moderator=self.request.user,
            action_type='warning',
            reason=warning.reason,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )


class BanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user bans"""
    serializer_class = BanSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        """Return all bans for moderators"""
        return Ban.objects.all()
    
    def perform_create(self, serializer):
        """Create ban and log the action"""
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
            ip_address=self.request.META.get('REMOTE_ADDR')
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
            ip_address=request.META.get('REMOTE_ADDR')
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
    
    reason = request.data.get('reason', 'No reason provided')
    user.is_active = False
    user.save()
    
    # Log the moderation action
    ModerationAction.objects.create(
        user=user,
        moderator=request.user,
        action_type='disable',
        reason=reason,
        ip_address=request.META.get('REMOTE_ADDR')
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
    user.is_active = True
    user.ban_expires_at = None
    user.ban_reason = ''
    user.save()
    
    # Log the moderation action
    ModerationAction.objects.create(
        user=user,
        moderator=request.user,
        action_type='enable',
        reason=reason,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return Response({
        'status': 'User account enabled successfully',
        'username': username
    })
