"""
User views
"""
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserRegistrationSerializer

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
