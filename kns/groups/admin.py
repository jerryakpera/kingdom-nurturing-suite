"""
Django admin configuration for the `groups` app.
"""

from django.contrib import admin

from .models import Group

admin.site.register(Group)
