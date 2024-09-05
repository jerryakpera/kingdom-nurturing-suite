"""
Admin configuration for the `vocations` app.
"""

from django.contrib import admin

from .models import Vocation

admin.site.register(Vocation)
