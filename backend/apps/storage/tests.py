"""
Unit tests for storage app
"""
import pytest
from unittest.mock import patch
from apps.storage.backends import SchematicStorage


class TestSchematicStorage:
    """Test SchematicStorage backend"""
    
    def test_storage_location(self):
        """Test that storage location is set correctly"""
        storage = SchematicStorage()
        
        assert storage.location == 'schematics'
    
    def test_storage_file_overwrite(self):
        """Test that file_overwrite is set to False"""
        storage = SchematicStorage()
        
        assert storage.file_overwrite == False
    
    @patch('apps.storage.backends.S3Boto3Storage.__init__')
    def test_storage_inherits_from_s3(self, mock_init):
        """Test that SchematicStorage inherits from S3Boto3Storage"""
        mock_init.return_value = None
        
        storage = SchematicStorage()
        
        # Verify it's a subclass
        from storages.backends.s3boto3 import S3Boto3Storage
        assert isinstance(storage, S3Boto3Storage)
