"""
Custom storage backends and utilities
"""
from storages.backends.s3boto3 import S3Boto3Storage


class SchematicStorage(S3Boto3Storage):
    """
    Custom storage class for schematic files (after scanning is complete and clean)
    """
    location = 'schematics'
    file_overwrite = False


class QuarantineStorage(S3Boto3Storage):
    """
    Isolated storage for files under virus scanning
    Files are stored here during scanning and moved to SchematicStorage if clean
    """
    location = 'quarantine'
    file_overwrite = False
    # More restrictive access settings
    default_acl = None  # No public access
    querystring_auth = True  # Always require signed URLs
