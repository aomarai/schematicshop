"""
Test configuration for pytest
"""
import os
import django
from django.conf import settings

# Set required environment variables for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schematicshop.settings')
os.environ.setdefault('DEBUG', '1')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('USE_S3', '0')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test-key')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test-secret')
os.environ.setdefault('AWS_STORAGE_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('CLAMAV_ENABLED', '0')
os.environ.setdefault('CLAMAV_HOST', 'localhost')
os.environ.setdefault('CLAMAV_PORT', '3310')
os.environ.setdefault('ALLOWED_HOSTS', '*')
os.environ.setdefault('CORS_ALLOWED_ORIGINS', 'http://localhost:3000')

def pytest_configure():
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.CLAMAV_ENABLED = False
    settings.USE_S3 = False
    
    # Disable caching for tests
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    
    django.setup()
