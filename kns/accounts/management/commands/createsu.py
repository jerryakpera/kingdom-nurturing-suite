from decouple import config
from django.core.management.base import BaseCommand
from kns.accounts.models import User


class Command(BaseCommand):
    """
    Create a superuser if none exist
    Example:
        manage.py createsuperuser_if_none_exists --user=admin --password=changeme
    """

    def handle(self, *args, **options):

        if User.objects.exists():
            return

        email = config("SU_EMAIL")
        password = config("SU_PASSWORD")

        User.objects.create_superuser(
            email=email,
            password=password,
        )

        self.stdout.write(f'User "{email}" was created')
