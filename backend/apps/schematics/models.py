"""
Schematic models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid

User = get_user_model()


class Tag(models.Model):
    """Tags for categorizing schematics"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Schematic(models.Model):
    """Main schematic model"""
    
    SCAN_STATUS_CHOICES = [
        ('pending', 'Pending Scan'),
        ('scanning', 'Scanning'),
        ('clean', 'Clean'),
        ('infected', 'Infected'),
        ('error', 'Scan Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schematics')
    
    # File information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='schematics/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['schematic', 'schem', 'litematic', 'nbt'])]
    )
    file_size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64, db_index=True)  # SHA-256 hash
    
    # Schematic metadata
    minecraft_version = models.CharField(max_length=20, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    block_count = models.IntegerField(null=True, blank=True)
    
    # Categorization
    tags = models.ManyToManyField(Tag, related_name='schematics', blank=True)
    category = models.CharField(max_length=50, blank=True, db_index=True)
    
    # Access control
    is_public = models.BooleanField(default=True)
    
    # Security scanning
    scan_status = models.CharField(
        max_length=20,
        choices=SCAN_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    scan_result = models.JSONField(null=True, blank=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Thumbnails and preview
    thumbnail_url = models.URLField(blank=True)
    preview_data = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['scan_status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def volume(self):
        if self.width and self.height and self.length:
            return self.width * self.height * self.length
        return None


class SchematicVersion(models.Model):
    """Version history for schematics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schematic = models.ForeignKey(Schematic, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='schematic_versions/%Y/%m/%d/')
    file_size = models.BigIntegerField()
    version_number = models.IntegerField()
    changelog = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['schematic', 'version_number']
    
    def __str__(self):
        return f"{self.schematic.title} v{self.version_number}"


class SchematicComment(models.Model):
    """Comments on schematics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schematic = models.ForeignKey(Schematic, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.schematic.title}"


class SchematicLike(models.Model):
    """Likes on schematics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schematic = models.ForeignKey(Schematic, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'schematic']
    
    def __str__(self):
        return f"{self.user.username} likes {self.schematic.title}"
