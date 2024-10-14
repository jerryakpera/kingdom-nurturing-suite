import factory
from django.utils import timezone

from kns.profiles.models import Profile


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "core.FAQ"

    question = factory.Faker("sentence", nb_words=10)
    answer = factory.Faker("paragraph", nb_sentences=3)


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "core.Notification"

    sender = factory.Iterator(Profile.objects.all())
    notification_type = factory.Faker(
        "random_element",
        elements=[
            "Group Move",
        ],
    )
    title = factory.Faker("sentence", nb_words=6)
    message = factory.Faker("paragraph", nb_sentences=2)
    link = factory.Faker("url")
    created_at = factory.LazyFunction(timezone.now)


class NotificationRecipientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "core.NotificationRecipient"
        skip_postgeneration_save = (
            True  # This will stop the automatic save after postgeneration hooks
        )

    notification = factory.SubFactory(
        NotificationFactory
    )  # Ensure NotificationFactory creates a valid notification
    recipient = factory.Iterator(Profile.objects.all())
    is_read = False
    read_at = None
