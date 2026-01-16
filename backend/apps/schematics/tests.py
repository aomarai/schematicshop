"""
Unit and integration tests for schematics app
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from apps.schematics.models import Schematic, Tag, SchematicComment, SchematicLike

User = get_user_model()


@pytest.mark.django_db
class TestSchematicModel:
    """Test Schematic model"""

    def test_create_schematic(self):
        """Test creating a schematic"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        schematic = Schematic.objects.create(
            owner=user,
            title='Test Schematic',
            description='A test schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='pending'
        )

        assert schematic.title == 'Test Schematic'
        assert schematic.owner == user
        assert schematic.scan_status == 'pending'
        assert str(schematic) == 'Test Schematic'

    def test_schematic_volume_property(self):
        """Test schematic volume calculation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        schematic = Schematic.objects.create(
            owner=user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            width=10,
            height=20,
            length=30
        )

        assert schematic.volume == 6000

    def test_schematic_without_dimensions(self):
        """Test schematic volume when dimensions are missing"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        schematic = Schematic.objects.create(
            owner=user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123'
        )

        assert schematic.volume is None


@pytest.mark.django_db
class TestTagModel:
    """Test Tag model"""

    def test_create_tag(self):
        """Test creating a tag"""
        tag = Tag.objects.create(
            name='medieval',
            slug='medieval'
        )

        assert tag.name == 'medieval'
        assert tag.slug == 'medieval'
        assert str(tag) == 'medieval'


@pytest.mark.django_db
class TestSchematicAPI:
    """Test Schematic API endpoints"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.list_url = reverse('schematic-list')

    def test_list_schematics_unauthenticated(self):
        """Test listing schematics without authentication"""
        # Create public schematic
        Schematic.objects.create(
            owner=self.user,
            title='Public Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 1

    def test_list_schematics_filters_infected(self):
        """Test that infected schematics are filtered out"""
        # Create infected schematic
        Schematic.objects.create(
            owner=self.user,
            title='Infected Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='infected'
        )

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_list_private_schematics_owner(self):
        """Test that owner can see private schematics"""
        self.client.force_authenticate(user=self.user)

        Schematic.objects.create(
            owner=self.user,
            title='Private Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=False,
            scan_status='clean'
        )

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_retrieve_schematic(self):
        """Test retrieving a schematic"""
        schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

        url = reverse('schematic-detail', kwargs={'pk': schematic.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Schematic'
        # View count should be incremented
        schematic.refresh_from_db()
        assert schematic.view_count == 1

    def test_create_schematic_authenticated(self):
        """Test creating a schematic while authenticated"""
        self.client.force_authenticate(user=self.user)

        # Create a simple file
        file_content = b'test content'
        test_file = SimpleUploadedFile(
            'test.schematic',
            file_content,
            content_type='application/octet-stream'
        )

        data = {
            'title': 'New Schematic',
            'description': 'Test description',
            'file': test_file,
            'is_public': True,
            'minecraft_version': '1.20.1'
        }

        response = self.client.post(self.list_url, data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        # Verify schematic was created with correct initial scan status
        # Note: Celery runs eagerly in tests, so scan completes immediately
        schematic = Schematic.objects.get(title='New Schematic')
        assert schematic.scan_status in ['pending', 'scanning', 'clean']  # Could be any of these in tests
        assert schematic.owner == self.user

    def test_create_schematic_unauthenticated(self):
        """Test creating a schematic without authentication"""
        file_content = b'test content'
        test_file = SimpleUploadedFile(
            'test.schematic',
            file_content,
            content_type='application/octet-stream'
        )

        data = {
            'title': 'New Schematic',
            'file': test_file
        }

        response = self.client.post(self.list_url, data, format='multipart')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_schematic(self):
        """Test updating own schematic"""
        self.client.force_authenticate(user=self.user)

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Original Title',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='clean'
        )

        url = reverse('schematic-detail', kwargs={'pk': schematic.id})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_cannot_update_others_schematic(self):
        """Test that users cannot update others' schematics"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        schematic = Schematic.objects.create(
            owner=other_user,
            title='Other User Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='clean'
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('schematic-detail', kwargs={'pk': schematic.id})
        data = {'title': 'Hacked Title'}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_schematic(self):
        """Test deleting own schematic"""
        self.client.force_authenticate(user=self.user)

        schematic = Schematic.objects.create(
            owner=self.user,
            title='To Delete',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='clean'
        )

        url = reverse('schematic-detail', kwargs={'pk': schematic.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Schematic.objects.filter(id=schematic.id).exists()


@pytest.mark.django_db
class TestSchematicDownload:
    """Test schematic download functionality"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_download_clean_schematic(self):
        """Test downloading a clean schematic"""
        self.client.force_authenticate(user=self.user)

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

        url = reverse('schematic-download', kwargs={'pk': schematic.id})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'download_url' in response.data
        assert 'file_name' in response.data

        # Check download count incremented
        schematic.refresh_from_db()
        assert schematic.download_count == 1

    def test_download_infected_schematic(self):
        """Test downloading an infected schematic is blocked"""
        self.client.force_authenticate(user=self.user)

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Infected Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='infected'
        )

        url = reverse('schematic-download', kwargs={'pk': schematic.id})
        response = self.client.post(url)

        # The view may return 403 or 404 depending on implementation
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestSchematicLikes:
    """Test schematic like functionality"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

    def test_like_schematic(self):
        """Test liking a schematic"""
        self.client.force_authenticate(user=self.user)

        url = reverse('schematic-like', kwargs={'pk': self.schematic.id})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert SchematicLike.objects.filter(user=self.user, schematic=self.schematic).exists()

    def test_unlike_schematic(self):
        """Test unliking a schematic"""
        self.client.force_authenticate(user=self.user)

        # First like it
        SchematicLike.objects.create(user=self.user, schematic=self.schematic)

        # Then unlike
        url = reverse('schematic-like', kwargs={'pk': self.schematic.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not SchematicLike.objects.filter(user=self.user, schematic=self.schematic).exists()

    def test_like_unauthenticated(self):
        """Test liking without authentication"""
        url = reverse('schematic-like', kwargs={'pk': self.schematic.id})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSchematicComments:
    """Test schematic comment functionality"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

    def test_get_comments(self):
        """Test getting comments for a schematic"""
        SchematicComment.objects.create(
            schematic=self.schematic,
            user=self.user,
            content='Great schematic!'
        )

        url = reverse('schematic-comments', kwargs={'pk': self.schematic.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['content'] == 'Great schematic!'

    def test_post_comment(self):
        """Test posting a comment"""
        self.client.force_authenticate(user=self.user)

        url = reverse('schematic-comments', kwargs={'pk': self.schematic.id})
        data = {'content': 'Nice work!'}
        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'Nice work!'
        assert SchematicComment.objects.filter(schematic=self.schematic).count() == 1

    def test_post_comment_unauthenticated(self):
        """Test posting a comment without authentication"""
        url = reverse('schematic-comments', kwargs={'pk': self.schematic.id})
        data = {'content': 'Nice work!'}
        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSchematicSearch:
    """Test schematic search functionality"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.list_url = reverse('schematic-list')

    def test_search_by_title(self):
        """Test searching schematics by title"""
        Schematic.objects.create(
            owner=self.user,
            title='Medieval Castle',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )
        Schematic.objects.create(
            owner=self.user,
            title='Modern House',
            file='test.schematic',
            file_size=1024,
            file_hash='abc124',
            is_public=True,
            scan_status='clean'
        )

        response = self.client.get(self.list_url, {'search': 'castle'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Castle' in response.data['results'][0]['title']

    def test_filter_by_category(self):
        """Test filtering schematics by category"""
        Schematic.objects.create(
            owner=self.user,
            title='Castle',
            category='medieval',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )
        Schematic.objects.create(
            owner=self.user,
            title='House',
            category='modern',
            file='test.schematic',
            file_size=1024,
            file_hash='abc124',
            is_public=True,
            scan_status='clean'
        )

        response = self.client.get(self.list_url, {'category': 'medieval'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['category'] == 'medieval'


@pytest.mark.django_db
class TestTrendingSchematics:
    """Test trending schematics endpoint"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_trending_schematics(self):
        """Test getting trending schematics"""
        # Create a schematic with likes and comments
        schematic = Schematic.objects.create(
            owner=self.user,
            title='Popular Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

        # Add likes
        SchematicLike.objects.create(user=self.user, schematic=schematic)

        # Add comment
        SchematicComment.objects.create(
            schematic=schematic,
            user=self.user,
            content='Great!'
        )

        url = reverse('schematic-trending')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0


@pytest.mark.django_db
class TestSchematicImages:
    """Test schematic image upload functionality"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            is_public=True,
            scan_status='clean'
        )

    def test_upload_image_authenticated(self):
        """Test uploading an image as the owner"""
        self.client.force_authenticate(user=self.user)

        # Create a simple test image
        from io import BytesIO
        from PIL import Image

        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        test_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )

        url = reverse('schematic-upload-image', kwargs={'pk': self.schematic.id})
        data = {
            'image': test_image,
            'caption': 'Test image',
            'order': 0
        }

        response = self.client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'image_url' in response.data
        assert response.data['caption'] == 'Test image'

    def test_upload_image_unauthenticated(self):
        """Test uploading an image without authentication"""
        from io import BytesIO
        from PIL import Image

        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        test_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )

        url = reverse('schematic-upload-image', kwargs={'pk': self.schematic.id})
        data = {'image': test_image}

        response = self.client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_image_not_owner(self):
        """Test uploading an image to someone else's schematic"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)

        from io import BytesIO
        from PIL import Image

        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        test_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )

        url = reverse('schematic-upload-image', kwargs={'pk': self.schematic.id})
        data = {'image': test_image}

        response = self.client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_images(self):
        """Test getting all images for a schematic"""
        from apps.schematics.models import SchematicImage

        # Create test images
        SchematicImage.objects.create(
            schematic=self.schematic,
            image='test1.png',
            caption='Image 1',
            order=0
        )
        SchematicImage.objects.create(
            schematic=self.schematic,
            image='test2.png',
            caption='Image 2',
            order=1
        )

        url = reverse('schematic-images', kwargs={'pk': self.schematic.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['caption'] == 'Image 1'

    def test_delete_image_owner(self):
        """Test deleting an image as the owner"""
        from apps.schematics.models import SchematicImage

        self.client.force_authenticate(user=self.user)

        image = SchematicImage.objects.create(
            schematic=self.schematic,
            image='test.png',
            caption='Test',
            order=0
        )

        url = reverse('schematic-delete-image', kwargs={'pk': self.schematic.id, 'image_id': image.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not SchematicImage.objects.filter(id=image.id).exists()

    def test_max_images_limit(self):
        """Test that max images limit is enforced"""
        from apps.schematics.models import SchematicImage

        self.client.force_authenticate(user=self.user)

        # Create 10 images (max limit)
        for i in range(10):
            SchematicImage.objects.create(
                schematic=self.schematic,
                image=f'test{i}.png',
                order=i
            )

        # Try to upload 11th image
        from io import BytesIO
        from PIL import Image

        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        test_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )

        url = reverse('schematic-upload-image', kwargs={'pk': self.schematic.id})
        data = {'image': test_image}

        response = self.client.post(url, data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Maximum' in str(response.data)
