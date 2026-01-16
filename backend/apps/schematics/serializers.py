"""
Schematic serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from PIL import Image
import io
from .models import Schematic, Tag, SchematicComment, SchematicLike, SchematicImage

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class SchematicOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']


class SchematicImageSerializer(serializers.ModelSerializer):
    """Serializer for schematic images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SchematicImage
        fields = ['id', 'image', 'image_url', 'caption', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_image(self, value):
        # File size validation (max 5MB for images)
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                "Image size must not exceed 5MB"
            )
        
        # Content-based validation - verify it's actually an image
        try:
            image = Image.open(value)
            image.verify()
            
            # Reset file pointer after verification
            value.seek(0)
            
            # Validate format is in allowed list (PIL uses 'JPEG' not 'JPG')
            allowed_formats = ['jpeg', 'png', 'webp']
            if image.format and image.format.lower() not in allowed_formats:
                raise serializers.ValidationError(
                    "Image format must be JPEG, PNG, or WebP"
                )
        except Exception as e:
            raise serializers.ValidationError(
                f"Invalid image file: {str(e)}"
            )
        
        return value


class SchematicListSerializer(serializers.ModelSerializer):
    """Serializer for listing schematics"""
    owner = SchematicOwnerSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    first_image = serializers.SerializerMethodField()
    images_count = serializers.IntegerField(source='images.count', read_only=True)

    class Meta:
        model = Schematic
        fields = [
            'id', 'title', 'description', 'owner', 'file_size',
            'minecraft_version', 'width', 'height', 'length',
            'tags', 'category', 'is_public', 'scan_status',
            'download_count', 'view_count', 'thumbnail_url',
            'likes_count', 'is_liked', 'first_image', 'images_count', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SchematicLike.objects.filter(user=request.user, schematic=obj).exists()
        return False
    
    def get_first_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return SchematicImageSerializer(first_image, context=self.context).data
        return None


class SchematicDetailSerializer(serializers.ModelSerializer):
    """Serializer for schematic details"""
    owner = SchematicOwnerSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    images = SchematicImageSerializer(many=True, read_only=True)

    class Meta:
        model = Schematic
        fields = [
            'id', 'title', 'description', 'owner', 'file', 'file_size', 'file_hash',
            'minecraft_version', 'width', 'height', 'length', 'block_count',
            'tags', 'tag_names', 'category', 'is_public', 'scan_status',
            'scan_result', 'scanned_at', 'download_count', 'view_count',
            'thumbnail_url', 'preview_data', 'likes_count', 'is_liked',
            'comments_count', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'file_size', 'file_hash', 'scan_status',
            'scan_result', 'scanned_at', 'download_count', 'view_count',
            'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SchematicLike.objects.filter(user=request.user, schematic=obj).exists()
        return False

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        schematic = Schematic.objects.create(**validated_data)

        # Add tags
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name.lower(),
                defaults={'slug': tag_name.lower().replace(' ', '-')}
            )
            schematic.tags.add(tag)

        return schematic

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided
        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_name.lower(),
                    defaults={'slug': tag_name.lower().replace(' ', '-')}
                )
                instance.tags.add(tag)

        return instance


class SchematicUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading schematics"""
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Schematic
        fields = ['title', 'description', 'file', 'tag_names', 'category', 'is_public', 'minecraft_version']

    def validate_file(self, value):
        # File size validation
        from django.conf import settings
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size must not exceed "
                f"{settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB"
            )

        # File extension validation
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in settings.ALLOWED_SCHEMATIC_EXTENSIONS:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: "
                f"{', '.join(settings.ALLOWED_SCHEMATIC_EXTENSIONS)}"
            )

        return value


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = SchematicOwnerSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = SchematicComment
        fields = ['id', 'user', 'content', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
