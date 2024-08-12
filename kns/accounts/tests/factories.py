import factory
import pytest


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.User"
