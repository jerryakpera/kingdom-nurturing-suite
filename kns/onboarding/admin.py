"""
Django admin site configuration for the `onboarding` app.
"""

from django.contrib import admin

from .models import ProfileOnboarding

admin.site.register(ProfileOnboarding)
