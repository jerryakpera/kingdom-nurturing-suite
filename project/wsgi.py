"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from project.settings import base

if base.DEBUG:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "project.settings.local",
    )
else:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "project.settings.production",
    )

application = get_wsgi_application()
