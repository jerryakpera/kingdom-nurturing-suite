from django.test import TestCase

from kns.custom_user.models import User

from ..db_data import classifications as predefined_classifications
from ..db_data import subclassifications as predefined_subclassifications
from ..models import Classification, Subclassification
from ..utils import populate_classifications, populate_subclassifications


class PopulateClassificationsAndSubclassificationsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data by creating a user and profile.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        # Define some predefined classifications and subclassifications for testing
        self.predefined_classifications = predefined_classifications
        self.predefined_subclassifications = predefined_subclassifications

    def test_classifications_are_created_correctly(self):
        """
        Test that classifications are created correctly based on predefined data.
        """
        populate_classifications(self.predefined_classifications)

        # Check that the correct number of classifications were created
        self.assertEqual(
            Classification.objects.count(),
            len(
                self.predefined_classifications,
            ),
        )

        # Check that each classification was created with the correct data
        for classification_data in self.predefined_classifications:
            classification = Classification.objects.get(
                title=classification_data["title"]
            )

            self.assertEqual(
                classification.content,
                classification_data["content"],
            )
            self.assertEqual(
                classification.author,
                self.profile,
            )

    def test_subclassifications_are_created_correctly(self):
        """
        Test that subclassifications are created correctly based on predefined data.
        """
        populate_subclassifications(self.predefined_subclassifications)

        # Check that the correct number of subclassifications were created
        self.assertEqual(
            Subclassification.objects.count(),
            len(
                self.predefined_subclassifications,
            ),
        )

        # Check that each subclassification was created with the correct data
        for subclassification_data in self.predefined_subclassifications:
            subclassification = Subclassification.objects.get(
                title=subclassification_data["title"],
            )
            self.assertEqual(
                subclassification.content,
                subclassification_data["content"],
            )
            self.assertEqual(subclassification.author, self.profile)

    def test_no_classifications_created_if_no_predefined_classifications(self):
        """
        Test that no classifications are created if the predefined classifications list is empty.
        """
        populate_classifications([])

        # Check that no classifications were created
        self.assertEqual(Classification.objects.count(), 0)

    def test_no_subclassifications_created_if_no_predefined_subclassifications(self):
        """
        Test that no subclassifications are created if the predefined
        subclassifications list is empty.
        """
        populate_subclassifications([])

        # Check that no subclassifications were created
        self.assertEqual(Subclassification.objects.count(), 0)

    def test_classification_is_not_created_if_exists(self):
        """
        Test that no duplicate classifications are created if a
        classification with the same title already exists.
        """
        # Create an initial classification
        Classification.objects.create(
            title="Beginner Classification",
            content="Introduction to basic concepts.",
            author=self.profile,
        )

        # Call the function with a classification that already exists
        populate_classifications(self.predefined_classifications)

        # Check that only one classification with the title "Beginner Classification" exists
        self.assertEqual(
            Classification.objects.filter(
                title="Beginner Classification",
            ).count(),
            1,
        )

    def test_subclassification_is_not_created_if_exists(self):
        """
        Test that no duplicate subclassifications are created if a subclassification with
        the same title already exists.
        """
        # Create an initial subclassification
        Subclassification.objects.create(
            title="Basic Concepts",
            content="Fundamentals of the subject.",
            author=self.profile,
        )

        # Call the function with a subclassification that already exists
        populate_subclassifications(self.predefined_subclassifications)

        # Check that only one subclassification with the title "Basic Concepts" exists
        self.assertEqual(
            Subclassification.objects.filter(
                title="Basic Concepts",
            ).count(),
            1,
        )

    def test_first_profile_is_set_as_author_for_classifications(self):
        """
        Test that the first profile in the database is set as the author
        for all created classifications.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_classifications(self.predefined_classifications)

        # Check that the first profile is used as the author for all classifications
        for classification in Classification.objects.all():
            self.assertEqual(classification.author, self.profile)

    def test_first_profile_is_set_as_author_for_subclassifications(self):
        """
        Test that the first profile in the database is set as the author
        for all created subclassifications.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="anotheruser@example.com",
            password="password",
        )

        # Call the function
        populate_subclassifications(self.predefined_subclassifications)

        # Check that the first profile is used as the author for all subclassifications
        for subclassification in Subclassification.objects.all():
            self.assertEqual(subclassification.author, self.profile)
