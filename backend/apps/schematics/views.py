"""
Schematic views
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
import hashlib

from .models import Schematic, Tag, SchematicComment, SchematicLike
from .serializers import (
    SchematicListSerializer, SchematicDetailSerializer,
    SchematicUploadSerializer, TagSerializer, CommentSerializer
)
from apps.scanning.tasks import scan_file_task


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners to edit"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.owner == request.user
        return obj.owner == request.user


class SchematicViewSet(viewsets.ModelViewSet):
    """ViewSet for schematic CRUD operations"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags__name', 'category']
    ordering_fields = ['created_at', 'download_count', 'view_count']
    filterset_fields = ['category', 'scan_status', 'is_public', 'owner']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SchematicListSerializer
        elif self.action == 'create':
            return SchematicUploadSerializer
        return SchematicDetailSerializer
    
    def get_queryset(self):
        queryset = Schematic.objects.select_related('owner').prefetch_related('tags', 'likes')
        
        # Filter based on user
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_public=True) | Q(owner=self.request.user)
            )
        else:
            queryset = queryset.filter(is_public=True)
        
        # Only show clean files
        queryset = queryset.exclude(scan_status='infected')
        
        return queryset
    
    def perform_create(self, serializer):
        # Calculate file hash
        file_obj = self.request.FILES['file']
        file_hash = hashlib.sha256()
        for chunk in file_obj.chunks():
            file_hash.update(chunk)
        
        # Save schematic
        schematic = serializer.save(
            owner=self.request.user,
            file_size=file_obj.size,
            file_hash=file_hash.hexdigest()
        )
        
        # Update user storage
        user = self.request.user
        user.storage_used += file_obj.size
        user.save()
        
        # Trigger virus scan
        scan_file_task.delay(str(schematic.id))
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Track downloads and return file URL"""
        schematic = self.get_object()
        
        # Check scan status
        if schematic.scan_status == 'infected':
            return Response(
                {'error': 'File flagged as infected'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment download count
        schematic.download_count += 1
        schematic.save(update_fields=['download_count'])
        
        return Response({
            'download_url': schematic.file.url,
            'file_name': schematic.file.name.split('/')[-1],
            'file_size': schematic.file_size
        })
    
    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        """Like or unlike a schematic"""
        schematic = self.get_object()
        
        if request.method == 'POST':
            like, created = SchematicLike.objects.get_or_create(
                user=request.user,
                schematic=schematic
            )
            if created:
                return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'already_liked'}, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            deleted, _ = SchematicLike.objects.filter(
                user=request.user,
                schematic=schematic
            ).delete()
            if deleted:
                return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
            return Response({'status': 'not_liked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or post comments"""
        schematic = self.get_object()
        
        if request.method == 'GET':
            comments = schematic.comments.filter(parent__isnull=True)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, schematic=schematic)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending schematics"""
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        queryset = self.get_queryset().filter(
            created_at__gte=week_ago
        ).annotate(
            popularity=Count('likes') + Count('comments')
        ).order_by('-popularity')[:20]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular tags"""
        tags = Tag.objects.annotate(
            schematic_count=Count('schematics')
        ).order_by('-schematic_count')[:20]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
