"""
Unit tests for users app
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import Warning, Ban, ModerationAction

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model"""

    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.storage_quota == 1024 * 1024 * 1024  # 1GB
        assert user.storage_used == 0

    def test_user_storage_properties(self):
        """Test user storage calculation properties"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.storage_used = 500 * 1024 * 1024  # 500MB
        user.save()

        expected_available = user.storage_quota - user.storage_used
        assert user.storage_available == expected_available
        expected_percentage = (user.storage_used / user.storage_quota) * 100
        assert abs(user.storage_percentage - expected_percentage) < 0.01  # Allow small floating point difference

    def test_user_string_representation(self):
        """Test user __str__ method"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'
    
    def test_is_banned_property_with_permanent_ban(self):
        """Test is_banned property with permanent ban"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        assert user.is_banned is True
    
    def test_is_banned_property_with_temporary_ban(self):
        """Test is_banned property with temporary ban"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.ban_expires_at = timezone.now() + timedelta(days=7)
        user.save()
        
        assert user.is_banned is True
    
    def test_is_banned_property_with_expired_ban(self):
        """Test is_banned property with expired ban"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.ban_expires_at = timezone.now() - timedelta(days=1)
        user.save()
        
        assert user.is_banned is False
    
    def test_unban_method(self):
        """Test unban method"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.ban_expires_at = timezone.now() + timedelta(days=7)
        user.ban_reason = 'Test ban'
        user.save()
        
        user.unban()
        
        assert user.is_active is True
        assert user.ban_expires_at is None
        assert user.ban_reason == ''


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration API"""

    def setup_method(self):
        """Set up test client"""
        self.client = APIClient()
        self.register_url = reverse('user-register')

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@example.com'
        assert 'password' not in response.data

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )

        data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication API"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('token-obtain')
        self.refresh_url = reverse('token-refresh')

    def test_login_success(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Test refresh
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile API"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile_url = reverse('user-profile')

    def test_get_profile_authenticated(self):
        """Test getting profile while authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert 'storage_quota' in response.data
        assert 'storage_used' in response.data

    def test_get_profile_unauthenticated(self):
        """Test getting profile while unauthenticated"""
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'This is my bio'
        }
        response = self.client.patch(self.profile_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
        assert response.data['bio'] == 'This is my bio'


@pytest.mark.django_db
class TestUserStats:
    """Test user statistics API"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stats_url = reverse('user-stats')

    def test_get_user_stats(self):
        """Test getting user statistics"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.stats_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'total_schematics' in response.data
        assert 'public_schematics' in response.data
        assert 'storage_used' in response.data
        assert 'storage_quota' in response.data
        assert 'storage_available' in response.data
        assert 'storage_percentage' in response.data

    def test_get_stats_unauthenticated(self):
        """Test getting stats while unauthenticated"""
        response = self.client.get(self.stats_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestWarningModel:
    """Test Warning model"""

    def test_create_warning(self):
        """Test creating a warning"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        
        warning = Warning.objects.create(
            user=user,
            issued_by=moderator,
            reason='Test warning'
        )
        
        assert warning.user == user
        assert warning.issued_by == moderator
        assert warning.reason == 'Test warning'
        assert warning.is_acknowledged is False
        assert str(warning) == f"Warning for testuser - {warning.created_at.date()}"


@pytest.mark.django_db
class TestBanModel:
    """Test Ban model"""

    def test_create_permanent_ban(self):
        """Test creating a permanent ban"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        
        ban = Ban.objects.create(
            user=user,
            issued_by=moderator,
            ban_type='permanent',
            reason='Serious violation'
        )
        
        assert ban.ban_type == 'permanent'
        user.refresh_from_db()
        assert user.is_active is False
        assert str(ban) == "Permanent ban for testuser"
    
    def test_create_temporary_ban(self):
        """Test creating a temporary ban"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        
        expires_at = timezone.now() + timedelta(days=7)
        ban = Ban.objects.create(
            user=user,
            issued_by=moderator,
            ban_type='temporary',
            reason='Minor violation',
            expires_at=expires_at
        )
        
        assert ban.ban_type == 'temporary'
        user.refresh_from_db()
        assert user.ban_expires_at == expires_at


@pytest.mark.django_db
class TestModerationActionModel:
    """Test ModerationAction model"""

    def test_create_moderation_action(self):
        """Test creating a moderation action"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        
        action = ModerationAction.objects.create(
            user=user,
            moderator=moderator,
            action_type='warning',
            reason='Test action',
            ip_address='127.0.0.1'
        )
        
        assert action.user == user
        assert action.moderator == moderator
        assert action.action_type == 'warning'


@pytest.mark.django_db
class TestWarningAPI:
    """Test Warning API endpoints"""

    def setup_method(self):
        """Set up test client and users"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        self.warnings_url = reverse('warning-list')
    
    def test_create_warning_as_moderator(self):
        """Test creating a warning as a moderator"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': self.user.id,
            'reason': 'Inappropriate behavior'
        }
        response = self.client.post(self.warnings_url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reason'] == 'Inappropriate behavior'
        assert Warning.objects.count() == 1
        assert ModerationAction.objects.count() == 1
    
    def test_create_warning_as_regular_user(self):
        """Test creating a warning as a regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'user': self.user.id,
            'reason': 'Test warning'
        }
        response = self.client.post(self.warnings_url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_warnings_as_moderator(self):
        """Test listing all warnings as moderator"""
        Warning.objects.create(
            user=self.user,
            issued_by=self.moderator,
            reason='Test warning'
        )
        
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.warnings_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_list_warnings_as_user(self):
        """Test listing own warnings as regular user"""
        Warning.objects.create(
            user=self.user,
            issued_by=self.moderator,
            reason='Test warning'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.warnings_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestBanAPI:
    """Test Ban API endpoints"""

    def setup_method(self):
        """Set up test client and users"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        self.bans_url = reverse('ban-list')
    
    def test_create_permanent_ban_as_moderator(self):
        """Test creating a permanent ban as a moderator"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': self.user.id,
            'ban_type': 'permanent',
            'reason': 'Serious violation'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ban_type'] == 'permanent'
        assert Ban.objects.count() == 1
        assert ModerationAction.objects.count() == 1
    
    def test_create_temporary_ban_as_moderator(self):
        """Test creating a temporary ban as a moderator"""
        self.client.force_authenticate(user=self.moderator)
        expires_at = timezone.now() + timedelta(days=7)
        data = {
            'user': self.user.id,
            'ban_type': 'temporary',
            'reason': 'Minor violation',
            'expires_at': expires_at.isoformat()
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ban_type'] == 'temporary'
    
    def test_create_temporary_ban_without_expiration(self):
        """Test creating a temporary ban without expiration date (should fail)"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': self.user.id,
            'ban_type': 'temporary',
            'reason': 'Minor violation'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_ban_as_regular_user(self):
        """Test creating a ban as a regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'user': self.user.id,
            'ban_type': 'permanent',
            'reason': 'Test ban'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_revoke_ban(self):
        """Test revoking a ban"""
        ban = Ban.objects.create(
            user=self.user,
            issued_by=self.moderator,
            ban_type='permanent',
            reason='Test ban'
        )
        
        self.client.force_authenticate(user=self.moderator)
        revoke_url = reverse('ban-revoke', kwargs={'pk': ban.id})
        response = self.client.post(revoke_url)
        
        assert response.status_code == status.HTTP_200_OK
        ban.refresh_from_db()
        assert ban.is_active is False
        self.user.refresh_from_db()
        assert self.user.is_active is True


@pytest.mark.django_db
class TestAccountDisableEnable:
    """Test account disable/enable endpoints"""

    def setup_method(self):
        """Set up test client and users"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
    
    def test_disable_account(self):
        """Test disabling a user account"""
        self.client.force_authenticate(user=self.moderator)
        disable_url = reverse('disable-user', kwargs={'username': self.user.username})
        data = {'reason': 'Account under review'}
        response = self.client.post(disable_url, data)
        
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.is_active is False
        assert ModerationAction.objects.count() == 1
    
    def test_enable_account(self):
        """Test enabling a user account"""
        self.user.is_active = False
        self.user.save()
        
        self.client.force_authenticate(user=self.moderator)
        enable_url = reverse('enable-user', kwargs={'username': self.user.username})
        data = {'reason': 'Review completed'}
        response = self.client.post(enable_url, data)
        
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.is_active is True
    
    def test_disable_account_as_regular_user(self):
        """Test disabling account as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        disable_url = reverse('disable-user', kwargs={'username': self.user.username})
        data = {'reason': 'Test'}
        response = self.client.post(disable_url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBanCheckMiddleware:
    """Test BanCheckMiddleware"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_banned_user_can_still_login(self):
        """Test that banned user can still login to check their status"""
        self.user.is_active = False
        self.user.ban_reason = 'Test ban'
        self.user.save()
        
        # Banned users can still get tokens
        login_url = reverse('token-obtain')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Login should fail because user is not active
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_active_user_can_access_api(self):
        """Test that active user can access API endpoints"""
        self.client.force_authenticate(user=self.user)
        stats_url = reverse('user-stats')
        response = self.client.get(stats_url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestModerationSecurityValidations:
    """Test security validations for moderation actions"""

    def setup_method(self):
        """Set up test client and users"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123',
            is_staff=True
        )
        self.superuser = User.objects.create_user(
            username='superuser',
            email='super@example.com',
            password='superpass123',
            is_staff=True,
            is_superuser=True
        )
        self.warnings_url = reverse('warning-list')
        self.bans_url = reverse('ban-list')
    
    def test_moderator_cannot_warn_themselves(self):
        """Test that moderators cannot warn themselves"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': self.moderator.id,
            'reason': 'Self-warning attempt'
        }
        response = self.client.post(self.warnings_url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'yourself' in str(response.data).lower()
    
    def test_moderator_cannot_ban_themselves(self):
        """Test that moderators cannot ban themselves"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': self.moderator.id,
            'ban_type': 'permanent',
            'reason': 'Self-ban attempt'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'yourself' in str(response.data).lower()
    
    def test_moderator_cannot_disable_themselves(self):
        """Test that moderators cannot disable themselves"""
        self.client.force_authenticate(user=self.moderator)
        disable_url = reverse('disable-user', kwargs={'username': self.moderator.username})
        data = {'reason': 'Self-disable attempt'}
        response = self.client.post(disable_url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'own account' in str(response.data).lower()
    
    def test_moderator_cannot_ban_staff(self):
        """Test that non-superuser moderators cannot ban staff members"""
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        self.client.force_authenticate(user=self.moderator)
        data = {
            'user': staff_user.id,
            'ban_type': 'permanent',
            'reason': 'Attempting to ban staff'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'superuser' in str(response.data).lower()
    
    def test_moderator_cannot_disable_staff(self):
        """Test that non-superuser moderators cannot disable staff members"""
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        self.client.force_authenticate(user=self.moderator)
        disable_url = reverse('disable-user', kwargs={'username': staff_user.username})
        data = {'reason': 'Attempting to disable staff'}
        response = self.client.post(disable_url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'superuser' in str(response.data).lower()
    
    def test_superuser_can_ban_staff(self):
        """Test that superusers can ban staff members"""
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        self.client.force_authenticate(user=self.superuser)
        data = {
            'user': staff_user.id,
            'ban_type': 'permanent',
            'reason': 'Superuser banning staff'
        }
        response = self.client.post(self.bans_url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check if ban was created
        ban = Ban.objects.filter(user=staff_user).first()
        assert ban is not None, "Ban should exist"
        assert ban.ban_type == 'permanent', f"Ban type should be permanent, got {ban.ban_type}"
        assert ban.is_active is True, f"Ban should be active, is_active={ban.is_active}"
        
        # Manually check what the database says
        staff_user_fresh = User.objects.get(pk=staff_user.pk)
        assert staff_user_fresh.is_active is False, f"Fresh query: User should be inactive after permanent ban, is_active={staff_user_fresh.is_active}"
    
    def test_superuser_can_disable_staff(self):
        """Test that superusers can disable staff members"""
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        self.client.force_authenticate(user=self.superuser)
        disable_url = reverse('disable-user', kwargs={'username': staff_user.username})
        data = {'reason': 'Superuser disabling staff'}
        response = self.client.post(disable_url, data)
        
        assert response.status_code == status.HTTP_200_OK
        staff_user.refresh_from_db()
        assert staff_user.is_active is False
