"""
Django admin site configuration for the accounts app.
"""

from django.contrib import admin

from .models import FAQ

admin.site.register(FAQ)
