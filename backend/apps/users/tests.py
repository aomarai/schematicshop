"""
Unit tests for users app
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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
