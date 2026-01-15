"""
Custom User model
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with additional fields
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.URLField(blank=True)
    storage_quota = models.BigIntegerField(default=1024*1024*1024)  # 1GB default
    storage_used = models.BigIntegerField(default=0)
    
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
