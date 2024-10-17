import random
from datetime import timedelta

import factory
from django.utils.text import slugify

from kns.events.models import Event
from kns.profiles.models import Profile


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Faker("sentence", nb_words=5)
    summary = factory.Faker("sentence", nb_words=10)
    cancel_reason = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("paragraph", nb_sentences=3)

    # Generate start_date within the specified range
    start_date = factory.Faker(
        "date_between",
        start_date="+1d",
        end_date="+30d",
    )

    # Generate end_date by adding a random number of days (1-30) to start_date
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=random.randint(1, 30))
    )

    registration_deadline_date = factory.Faker(
        "date_between", start_date="-5d", end_date="+1d"
    )
    refreshments = factory.Faker("boolean")
    accommodation = factory.Faker("boolean")
    event_contact_name = factory.Faker("name")
    event_contact_email = factory.Faker("email")
    registration_limit = factory.Faker("random_int", min=1, max=100)
    archived_at = None
    author = factory.Iterator(Profile.objects.all())

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
