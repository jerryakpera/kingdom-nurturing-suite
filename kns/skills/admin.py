"""
Django admin site configuration for the skills app.
"""

from django.contrib import admin

from .models import Skill

# Register the Skill model with the admin site
admin.site.register(Skill)
