"""
Custom storage backends and utilities
"""
from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage


class SchematicStorage(S3Boto3Storage):
    """
    Custom storage class for schematic files
    """
    location = 'schematics'
    file_overwrite = False
