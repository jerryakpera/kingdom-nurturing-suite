import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "custom_user.User"

    email = factory.Faker("email")
