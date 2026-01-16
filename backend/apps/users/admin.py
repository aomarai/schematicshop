"""
User admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import User, Warning, Ban, ModerationAction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'storage_used', 
                    'storage_quota', 'is_staff', 'is_banned_display', 'ban_status']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Storage', {'fields': ('storage_quota', 'storage_used', 'infected_upload_count')}),
        ('Profile', {'fields': ('bio', 'avatar')}),
        ('Moderation', {'fields': ('ban_expires_at', 'ban_reason')}),
    )
    
    def is_banned_display(self, obj):
        """Display ban status with color"""
        if obj.is_banned:
            return format_html('<span style="color: red; font-weight: bold;">🚫 Banned</span>')
        return format_html('<span style="color: green;">✓ Active</span>')
    is_banned_display.short_description = 'Ban Status'
    
    def ban_status(self, obj):
        """Display detailed ban status"""
        if not obj.is_active:
            return 'Permanently Disabled'
        if obj.ban_expires_at and obj.ban_expires_at > timezone.now():
            return f'Temp Ban until {obj.ban_expires_at.strftime("%Y-%m-%d %H:%M")}'
        return 'Not Banned'
    ban_status.short_description = 'Ban Details'


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'issued_by_link', 'reason_short', 
                    'is_acknowledged', 'created_at']
    list_filter = ['is_acknowledged', 'created_at']
    search_fields = ['user__username', 'issued_by__username', 'reason']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'issued_by']
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def issued_by_link(self, obj):
        """Link to moderator admin page"""
        if obj.issued_by:
            url = reverse('admin:users_user_change', args=[obj.issued_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.issued_by.username)
        return '-'
    issued_by_link.short_description = 'Issued By'
    
    def reason_short(self, obj):
        """Display truncated reason"""
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Reason'


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'ban_type', 'issued_by_link', 
                    'is_active', 'expires_at', 'created_at']
    list_filter = ['ban_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'issued_by__username', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'issued_by']
    
    fieldsets = (
        ('Ban Details', {
            'fields': ('user', 'ban_type', 'reason', 'is_active')
        }),
        ('Timing', {
            'fields': ('expires_at', 'created_at', 'updated_at')
        }),
        ('Issued By', {
            'fields': ('issued_by',)
        }),
    )
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def issued_by_link(self, obj):
        """Link to moderator admin page"""
        if obj.issued_by:
            url = reverse('admin:users_user_change', args=[obj.issued_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.issued_by.username)
        return '-'
    issued_by_link.short_description = 'Issued By'


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'action_type', 'user_link', 'moderator_link', 
                    'reason_short', 'ip_address', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'moderator__username', 'reason', 'ip_address']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'moderator']
    
    fieldsets = (
        ('Action Details', {
            'fields': ('action_type', 'reason', 'details')
        }),
        ('Users', {
            'fields': ('user', 'moderator')
        }),
        ('Additional Info', {
            'fields': ('ip_address', 'created_at')
        }),
    )
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def moderator_link(self, obj):
        """Link to moderator admin page"""
        if obj.moderator:
            url = reverse('admin:users_user_change', args=[obj.moderator.id])
            return format_html('<a href="{}">{}</a>', url, obj.moderator.username)
        return '-'
    moderator_link.short_description = 'Moderator'
    
    def reason_short(self, obj):
        """Display truncated reason"""
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Reason'
