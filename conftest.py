"""
This module contains configuration and fixtures for pytest.

Fixtures in this module are used to set up a clean database state
for tests by utilizing pytest-django's database fixture.
"""

import pytest


@pytest.fixture(autouse=True)
def aaa_db(db):
    """
    Fixture to provide a fresh database for tests.

    This fixture is automatically used for all tests, ensuring a clean
    database state. It relies on the `db` fixture from pytest-django
    for setup.

    Parameters
    ----------
    db : pytest_django.fixtures.django_db
        The database fixture from pytest-django which provides a
        database setup for the tests.
    """
    pass
