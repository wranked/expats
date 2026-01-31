import pytest

from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_db",
        "ATOMIC_REQUESTS": True,
    }
    # Ensure all databases have ATOMIC_REQUESTS
    for db_config in settings.DATABASES.values():
        db_config.setdefault('ATOMIC_REQUESTS', True)
