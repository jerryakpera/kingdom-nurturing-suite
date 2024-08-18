import factory


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "core.FAQ"

    question = factory.Faker("sentence", nb_words=10)
    answer = factory.Faker("paragraph", nb_sentences=3)
