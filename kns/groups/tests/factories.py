from uuid import uuid4

import factory

from kns.groups.models import Group, GroupMember
from kns.profiles.models import Profile


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Faker("company")
    slug = factory.LazyFunction(uuid4)
    description = factory.Faker(
        "paragraph",
        nb_sentences=5,
    )
    leader = factory.Iterator(Profile.objects.all())
    parent = None
    location_country = factory.Faker("country")
    location_city = factory.Faker("city")


class GroupMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupMember

    profile = factory.Iterator(Profile.objects.all())
    group = factory.SubFactory(GroupFactory)
