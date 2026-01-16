"""
Tests for test data management commands
"""
import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model
from apps.schematics.models import Schematic, Tag

User = get_user_model()


@pytest.mark.django_db
class TestLoadTestSchematicsCommand:
    """Test load_test_schematics management command"""

    def test_load_creates_test_data(self):
        """Test that load_test_schematics creates test data"""
        # Initially no test data
        assert Schematic.objects.filter(title__startswith='[TEST]').count() == 0
        
        # Load test data
        call_command('load_test_schematics')
        
        # Verify data created
        assert Schematic.objects.filter(title__startswith='[TEST]').count() == 8
        assert User.objects.filter(username__startswith='testuser').count() == 3
        assert Tag.objects.count() >= 8
        
        # Check sample schematic
        castle = Schematic.objects.get(title='[TEST] Medieval Castle')
        assert castle.width == 64
        assert castle.height == 45
        assert castle.length == 64
        assert castle.scan_status == 'clean'
        assert castle.tags.filter(name='medieval').exists()

    def test_load_with_clear_flag(self):
        """Test that --clear flag removes existing test data"""
        # Load initial data
        call_command('load_test_schematics')
        initial_count = Schematic.objects.count()
        
        # Load again with --clear
        call_command('load_test_schematics', '--clear')
        
        # Should have same count (cleared and reloaded)
        assert Schematic.objects.count() == initial_count

    def test_load_is_idempotent(self):
        """Test that loading twice doesn't duplicate data"""
        call_command('load_test_schematics')
        first_count = Schematic.objects.filter(title__startswith='[TEST]').count()
        
        # Load again without --clear
        call_command('load_test_schematics')
        second_count = Schematic.objects.filter(title__startswith='[TEST]').count()
        
        # Count should be the same (no duplicates)
        assert first_count == second_count


@pytest.mark.django_db
class TestClearTestSchematicsCommand:
    """Test clear_test_schematics management command"""

    def test_clear_removes_test_data(self):
        """Test that clear_test_schematics removes test data"""
        # Load test data
        call_command('load_test_schematics')
        assert Schematic.objects.filter(title__startswith='[TEST]').count() > 0
        
        # Clear test data
        call_command('clear_test_schematics')
        
        # Verify data removed
        assert Schematic.objects.filter(title__startswith='[TEST]').count() == 0

    def test_clear_preserves_non_test_data(self):
        """Test that clear doesn't remove non-test data"""
        # Create a non-test user and schematic
        user = User.objects.create_user(
            username='realuser',
            email='real@example.com',
            password='realpass123'
        )
        real_schematic = Schematic.objects.create(
            owner=user,
            title='Real Schematic',
            description='A real schematic',
            file='real.schematic',
            file_size=1024,
            file_hash='realhahs123'
        )
        
        # Load and clear test data
        call_command('load_test_schematics')
        call_command('clear_test_schematics')
        
        # Real data should still exist
        assert Schematic.objects.filter(title='Real Schematic').exists()
        assert User.objects.filter(username='realuser').exists()
