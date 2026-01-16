"""
User serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Warning, Ban, ModerationAction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    storage_available = serializers.ReadOnlyField()
    storage_percentage = serializers.ReadOnlyField()
    is_banned = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar', 'storage_quota', 'storage_used',
            'storage_available', 'storage_percentage', 'created_at',
            'is_banned', 'ban_expires_at', 'ban_reason'
        ]
        read_only_fields = [
            'id', 'storage_used', 'created_at', 
            'is_banned', 'ban_expires_at', 'ban_reason'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class WarningSerializer(serializers.ModelSerializer):
    """Serializer for user warnings"""
    issued_by_username = serializers.CharField(source='issued_by.username', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Warning
        fields = ['id', 'user', 'user_username', 'issued_by', 'issued_by_username', 
                  'reason', 'is_acknowledged', 'created_at']
        read_only_fields = ['id', 'issued_by', 'created_at']


class BanSerializer(serializers.ModelSerializer):
    """Serializer for user bans"""
    issued_by_username = serializers.CharField(source='issued_by.username', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Ban
        fields = ['id', 'user', 'user_username', 'issued_by', 'issued_by_username',
                  'ban_type', 'reason', 'expires_at', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'issued_by', 'is_active', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate ban data"""
        # Get ban_type from attrs or from instance if it's an update
        ban_type = attrs.get('ban_type')
        if not ban_type and self.instance:
            ban_type = self.instance.ban_type
        
        expires_at = attrs.get('expires_at')
        
        if ban_type == 'temporary':
            if not expires_at:
                raise serializers.ValidationError({
                    'expires_at': 'Expiration date is required for temporary bans'
                })
            if expires_at <= timezone.now():
                raise serializers.ValidationError({
                    'expires_at': 'Expiration date must be in the future'
                })
        
        if ban_type == 'permanent' and expires_at:
            raise serializers.ValidationError({
                'expires_at': 'Permanent bans should not have an expiration date'
            })
        
        return attrs


class ModerationActionSerializer(serializers.ModelSerializer):
    """Serializer for moderation action audit log"""
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ModerationAction
        fields = ['id', 'user', 'user_username', 'moderator', 'moderator_username',
                  'action_type', 'reason', 'details', 'ip_address', 'created_at']
        read_only_fields = ['id', 'moderator', 'created_at']
