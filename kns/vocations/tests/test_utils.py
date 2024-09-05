from django.test import TestCase

from kns.custom_user.models import User

from ..models import Vocation
from ..utils import populate_vocations
from ..vocations_data import vocations as predefined_vocations


class PopulateVocationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        # Modify predefined_vocations for testing if necessary
        self.predefined_vocations = predefined_vocations

    def test_vocations_are_created_correctly(self):
        # Override the vocations in the module with test data

        # Call the function
        populate_vocations(self.predefined_vocations)

        # Check that the correct number of vocations were created
        self.assertEqual(
            Vocation.objects.count(),
            len(self.predefined_vocations),
        )

        # Check that each vocation was created with the correct data
        for i, vocation_data in enumerate(self.predefined_vocations):
            vocation = Vocation.objects.get(
                title=vocation_data["title"],
            )
            self.assertEqual(
                vocation.description,
                vocation_data["description"],
            )
            self.assertEqual(vocation.author, self.profile)

    def test_no_vocations_created_if_no_predefined_vocations(self):
        # Override the vocations in the module with an empty list
        self.predefined_vocations = []

        # Call the function
        populate_vocations(self.predefined_vocations)

        # Check that no vocations were created
        self.assertEqual(Vocation.objects.count(), 0)

    def test_first_profile_is_set_as_author(self):
        # Ensure there is more than one profile in the database
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_vocations(self.predefined_vocations)

        # Check that the first profile is set as the author for all vocations
        for vocation in Vocation.objects.all():
            self.assertEqual(vocation.author, self.profile)
