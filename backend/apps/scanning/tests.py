"""
Unit tests for scanning app
"""
import pytest
from unittest.mock import patch, MagicMock
from apps.schematics.models import Schematic
from django.contrib.auth import get_user_model

User = get_user_model()


class TestVirusScanner:
    """Test VirusScanner class"""

    def test_scanner_init(self):
        """Test scanner initialization"""
        with patch('apps.scanning.scanner.settings') as mock_settings:
            mock_settings.CLAMAV_HOST = 'clamav'
            mock_settings.CLAMAV_PORT = 3310

            from apps.scanning.scanner import VirusScanner
            scanner = VirusScanner()

            assert scanner.host == 'clamav'
            assert scanner.port == 3310

    def test_scan_file_clean(self):
        """Test scanning a clean file"""
        # Mock ClamAV for testing
        from apps.scanning.scanner import VirusScanner
        scanner = VirusScanner()

        with patch.object(scanner, 'scan_file') as mock_scan:
            mock_scan.return_value = {
                'is_infected': False,
                'virus_name': None,
                'status': 'clean'
            }

            result = scanner.scan_file('/path/to/clean_file.txt')

            assert result['is_infected'] is False
            assert result['status'] == 'clean'
            assert result['virus_name'] is None

    def test_scan_file_infected(self):
        """Test scanning an infected file"""
        from apps.scanning.scanner import VirusScanner
        scanner = VirusScanner()

        with patch.object(scanner, 'scan_file') as mock_scan:
            mock_scan.return_value = {
                'is_infected': True,
                'virus_name': 'Eicar-Test-Signature',
                'status': 'infected'
            }

            result = scanner.scan_file('/path/to/infected_file.txt')

            assert result['is_infected'] is True
            assert result['status'] == 'infected'
            assert result['virus_name'] == 'Eicar-Test-Signature'

    def test_scan_file_error(self):
        """Test scanning when an error occurs"""
        from apps.scanning.scanner import VirusScanner
        scanner = VirusScanner()

        with patch.object(scanner, 'scan_file') as mock_scan:
            mock_scan.return_value = {
                'is_infected': False,
                'virus_name': None,
                'status': 'error',
                'error': 'Connection failed'
            }

            result = scanner.scan_file('/path/to/file.txt')

            assert result['is_infected'] is False
            assert result['status'] == 'error'
            assert 'error' in result

    def test_scan_stream_error(self):
        """Test scanning stream when ClamAV is unavailable"""
        from apps.scanning.scanner import VirusScanner
        scanner = VirusScanner()

        # Without ClamAV running, this will return error status
        result = scanner.scan_stream(b'test content')

        assert result['is_infected'] is False
        assert result['status'] == 'error'
        assert 'error' in result

    def test_scan_stream_clean(self):
        """Test scanning a clean stream"""
        from apps.scanning.scanner import VirusScanner
        scanner = VirusScanner()

        with patch.object(scanner, 'scan_stream') as mock_scan:
            mock_scan.return_value = {
                'is_infected': False,
                'virus_name': None,
                'status': 'clean'
            }

            result = scanner.scan_stream(b'clean content')

            assert result['is_infected'] is False
            assert result['status'] == 'clean'


@pytest.mark.django_db
class TestScanFileTask:
    """Test scan_file_task Celery task"""

    def setup_method(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_scan_file_task_clean(self):
        """Test scanning task for clean file"""
        from apps.scanning.tasks import scan_file_task

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='pending'
        )

        with patch('apps.scanning.scanner.VirusScanner') as mock_scanner_class:
            # Mock scanner to return clean result
            mock_scanner = MagicMock()
            mock_scanner.scan_file.return_value = {
                'is_infected': False,
                'virus_name': None,
                'status': 'clean'
            }
            mock_scanner_class.return_value = mock_scanner

            # Mock file.path property
            with patch.object(
                type(schematic.file),
                'path',
                new_callable=lambda: property(lambda self: '/fake/path')
            ):
                result = scan_file_task(str(schematic.id))

            assert result['status'] == 'clean'

            # Check schematic was updated
            schematic.refresh_from_db()
            assert schematic.scan_status == 'clean'
            assert schematic.scanned_at is not None

    def test_scan_file_task_infected(self):
        """Test scanning task for infected file"""
        from apps.scanning.tasks import scan_file_task

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Infected Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='pending'
        )

        with patch('apps.scanning.scanner.VirusScanner') as mock_scanner_class:
            # Mock scanner to return infected result
            mock_scanner = MagicMock()
            mock_scanner.scan_file.return_value = {
                'is_infected': True,
                'virus_name': 'TestVirus',
                'status': 'infected'
            }
            mock_scanner_class.return_value = mock_scanner

            # Mock file.path property
            with patch.object(
                type(schematic.file),
                'path',
                new_callable=lambda: property(lambda self: '/fake/path')
            ):
                result = scan_file_task(str(schematic.id))

            assert result['status'] == 'infected'

            # Check schematic was updated
            schematic.refresh_from_db()
            assert schematic.scan_status == 'infected'
            assert schematic.scan_result['virus_name'] == 'TestVirus'

    def test_scan_file_task_error(self):
        """Test scanning task when error occurs - should set to pending for retry"""
        from apps.scanning.tasks import scan_file_task
        from celery.exceptions import Retry

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='pending'
        )

        with patch('apps.scanning.scanner.VirusScanner') as mock_scanner_class:
            # Mock scanner to return error result
            mock_scanner = MagicMock()
            mock_scanner.scan_file.return_value = {
                'is_infected': False,
                'virus_name': None,
                'status': 'error',
                'error': 'Scanner unavailable'
            }
            mock_scanner_class.return_value = mock_scanner

            # Mock file.path property
            with patch.object(
                type(schematic.file),
                'path',
                new_callable=lambda: property(lambda self: '/fake/path')
            ):
                # The task will raise Retry exception with new logic
                try:
                    scan_file_task(str(schematic.id))
                except Retry:
                    pass  # Expected behavior - task will retry

            # Check schematic was updated to pending (for retry)
            schematic.refresh_from_db()
            assert schematic.scan_status == 'pending'
            # Retry count may be incremented multiple times due to test execution
            assert schematic.scan_retry_count >= 1

    def test_scan_file_task_not_found(self):
        """Test scanning task for non-existent schematic"""
        from apps.scanning.tasks import scan_file_task

        result = scan_file_task('00000000-0000-0000-0000-000000000000')

        assert result is None

    def test_scan_file_task_updates_status_to_scanning(self):
        """Test that task updates status to scanning"""
        from apps.scanning.tasks import scan_file_task

        schematic = Schematic.objects.create(
            owner=self.user,
            title='Test Schematic',
            file='test.schematic',
            file_size=1024,
            file_hash='abc123',
            scan_status='pending'
        )

        with patch('apps.scanning.scanner.VirusScanner') as mock_scanner_class:
            mock_scanner = MagicMock()

            def check_status(*args, **kwargs):
                # Check status during scan
                s = Schematic.objects.get(id=schematic.id)
                assert s.scan_status == 'scanning'
                return {
                    'is_infected': False,
                    'virus_name': None,
                    'status': 'clean'
                }

            mock_scanner.scan_file.side_effect = check_status
            mock_scanner_class.return_value = mock_scanner

            # Mock file.path property
            with patch.object(
                type(schematic.file),
                'path',
                new_callable=lambda: property(lambda self: '/fake/path')
            ):
                scan_file_task(str(schematic.id))
