"""
Django admin site configuration for the core app.
"""

from django.contrib import admin

from .models import FAQ, Setting

# Registering the FAQ model with the admin site
admin.site.register(FAQ)

# Registering the Setting model with the admin site
admin.site.register(Setting)
