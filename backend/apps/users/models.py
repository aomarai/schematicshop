"""
Custom User model
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model with additional fields
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.URLField(blank=True)
    storage_quota = models.BigIntegerField(
        default=1024 * 1024 * 1024
    )  # 1GB default
    storage_used = models.BigIntegerField(default=0)
    infected_upload_count = models.IntegerField(
        default=0
    )  # Track infected file uploads
    
    # Moderation fields
    ban_expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    ban_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def storage_available(self):
        return self.storage_quota - self.storage_used

    @property
    def storage_percentage(self):
        if self.storage_quota == 0:
            return 0
        return (self.storage_used / self.storage_quota) * 100
    
    @property
    def is_banned(self):
        """Check if user is currently banned"""
        if not self.is_active:
            return True
        if self.ban_expires_at:
            # Only consider it a ban if the expiration is in the future
            if self.ban_expires_at > timezone.now():
                return True
        return False
    
    def unban(self):
        """Unban the user by clearing ban-related fields"""
        self.is_active = True
        self.ban_expires_at = None
        self.ban_reason = ''
        self.save()


class Warning(models.Model):
    """
    User warning for violations of community guidelines
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='warnings_issued')
    reason = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Warning for {self.user.username} - {self.created_at.date()}"


class Ban(models.Model):
    """
    User ban (temporary or permanent)
    """
    BAN_TYPE_CHOICES = [
        ('temporary', 'Temporary'),
        ('permanent', 'Permanent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bans')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bans_issued')
    ban_type = models.CharField(max_length=20, choices=BAN_TYPE_CHOICES)
    reason = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ban_type.title()} ban for {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Apply ban to user when created"""
        is_new = self.pk is None
        
        if is_new and self.is_active:
            # First save the ban record
            super().save(*args, **kwargs)
            
            # Then apply ban to user using update() for atomicity
            if self.ban_type == 'permanent':
                User.objects.filter(pk=self.user.pk).update(
                    is_active=False,
                    ban_expires_at=None,
                    ban_reason=self.reason
                )
            else:
                User.objects.filter(pk=self.user.pk).update(
                    ban_expires_at=self.expires_at,
                    ban_reason=self.reason
                )
        else:
            # For updates, just save the ban record without modifying user
            super().save(*args, **kwargs)


class ModerationAction(models.Model):
    """
    Audit log for all moderation actions
    """
    ACTION_TYPE_CHOICES = [
        ('warning', 'Warning Issued'),
        ('ban', 'Ban Issued'),
        ('unban', 'Ban Removed'),
        ('disable', 'Account Disabled'),
        ('enable', 'Account Enabled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderation_actions_taken')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    reason = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.user.username} by {self.moderator}"
