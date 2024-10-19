"""
Factories for the `activities` app.
"""

import random
from datetime import date, datetime, timedelta
from uuid import uuid4

import factory
from django.utils import timezone
from django.utils.text import slugify

from kns.activities.models import (
    Activity,
    ActivityAttendance,
    ActivityFacilitator,
    ActivityFacilitatorInvitation,
    ActivityFeedback,
    ActivityRegistration,
)
from kns.events.tests.factories import EventFactory
from kns.profiles.models import Profile


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    title = factory.Faker("sentence", nb_words=5)
    summary = factory.Faker("sentence", nb_words=10)
    description = factory.Faker("paragraph", nb_sentences=3)

    # Generating a related event using the EventFactory
    event = factory.SubFactory(EventFactory)

    activity_type = factory.Iterator(
        [
            "skill_training",
            "movement_training",
            "community_service",
            "prayer_movement",
        ]
    )
    start_date = factory.Faker(
        "date_between",
        start_date="+1d",
        end_date="+30d",
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=random.randint(1, 3))
    )

    start_time = factory.Faker("time_object")
    end_time = factory.LazyAttribute(
        lambda o: (
            datetime.combine(date.today(), o.start_time)
            + timedelta(hours=random.randint(1, 3))
        ).time()
    )

    capacity = factory.Faker(
        "random_int",
        min=1,
        max=100,
    )
    author = factory.Iterator(Profile.objects.all())

    scope = factory.Iterator(
        [
            "comprehensive",
            "abridged",
        ]
    )
    beneficiary = factory.Faker("name")

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)


class ActivityRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityRegistration

    activity = factory.SubFactory(ActivityFactory)
    profile = factory.Iterator(Profile.objects.all())
    status = factory.Iterator(
        [choice[0] for choice in ActivityRegistration.STATUS_CHOICES]
    )
    guest_name = factory.Faker("name", locale="en_US")
    guest_email = factory.Faker("email")
    is_guest = factory.Faker("boolean", chance_of_getting_true=50)
    confirmation_token = factory.LazyFunction(uuid4)
    rejection_token = factory.LazyFunction(uuid4)


class ActivityFacilitatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityFacilitator

    activity = factory.SubFactory(ActivityFactory)
    facilitator = factory.Iterator(Profile.objects.all())


class ActivityFacilitatorInvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityFacilitatorInvitation

    activity = factory.SubFactory(ActivityFactory)
    facilitator = factory.Iterator(Profile.objects.all())
    status = factory.Iterator(
        [choice[0] for choice in ActivityFacilitator.STATUS_CHOICES]
    )
    invitation_message = factory.Faker("text")


class ActivityFeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityFeedback

    activity = factory.SubFactory(ActivityFactory)
    profile = factory.Iterator(Profile.objects.all())
    rating = factory.Faker("random_int", min=1, max=5)
    comment = factory.Faker("text", max_nb_chars=200)
