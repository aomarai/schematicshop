"""
Schematic admin
"""
from django.contrib import admin
from .models import Schematic, Tag, SchematicComment, SchematicLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Schematic)
class SchematicAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'file_size', 'scan_status',
        'is_public', 'download_count', 'view_count', 'created_at'
    ]
    list_filter = ['scan_status', 'is_public', 'category', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    readonly_fields = ['id', 'file_hash', 'download_count', 'view_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']


@admin.register(SchematicComment)
class SchematicCommentAdmin(admin.ModelAdmin):
    list_display = ['schematic', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'schematic__title', 'user__username']


@admin.register(SchematicLike)
class SchematicLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'schematic', 'created_at']
    list_filter = ['created_at']
