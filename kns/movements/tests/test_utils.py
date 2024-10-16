from django.test import TestCase

from kns.custom_user.models import User

from ..db_data import movement_topics as predefined_movement_topics
from ..db_data import movements as predefined_movements
from ..models import Movement, MovementTopic
from ..utils import populate_movement_topics, populate_movements


class PopulateMovementsAndTopicsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data by creating a user and profile.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        # Define some predefined movements and movement topics for testing
        self.predefined_movements = predefined_movements
        self.predefined_movement_topics = predefined_movement_topics

    def test_movements_are_created_correctly(self):
        """
        Test that movements are created correctly based on predefined data.
        """
        populate_movements(self.predefined_movements)

        # Check that the correct number of movements were created
        self.assertEqual(
            Movement.objects.count(),
            len(self.predefined_movements),
        )

        # Check that each movement was created with the correct data
        for movement_data in self.predefined_movements:
            movement = Movement.objects.get(title=movement_data["title"])
            self.assertEqual(movement.content, movement_data["content"])
            self.assertEqual(movement.author, self.profile)

    def test_movement_topics_are_created_correctly(self):
        """
        Test that movement topics are created correctly based on predefined data.
        """
        populate_movement_topics(self.predefined_movement_topics)

        # Check that the correct number of movement topics were created
        self.assertEqual(
            MovementTopic.objects.count(),
            len(self.predefined_movement_topics),
        )

        # Check that each movement topic was created with the correct data
        for movement_topic_data in self.predefined_movement_topics:
            movement_topic = MovementTopic.objects.get(
                title=movement_topic_data["title"],
            )
            self.assertEqual(movement_topic.content, movement_topic_data["content"])
            self.assertEqual(movement_topic.author, self.profile)

    def test_no_movements_created_if_no_predefined_movements(self):
        """
        Test that no movements are created if the predefined movements list is empty.
        """
        populate_movements([])

        # Check that no movements were created
        self.assertEqual(Movement.objects.count(), 0)

    def test_no_movement_topics_created_if_no_predefined_movement_topics(self):
        """
        Test that no movement topics are created if the predefined movement topics list is empty.
        """
        populate_movement_topics([])

        # Check that no movement topics were created
        self.assertEqual(MovementTopic.objects.count(), 0)

    def test_movement_is_not_created_if_exists(self):
        """
        Test that no duplicate movements are created if a movement
        with the same title already exists.
        """
        # Create an initial movement
        Movement.objects.create(
            title="Evangelism Movement",
            content="Teaching the principles of evangelism.",
            author=self.profile,
        )

        # Call the function with a movement that already exists
        populate_movements(self.predefined_movements)

        # Check that only one movement with the title "Evangelism Movement" exists
        self.assertEqual(
            Movement.objects.filter(title="Evangelism Movement").count(),
            1,
        )

    def test_movement_topic_is_not_created_if_exists(self):
        """
        Test that no duplicate movement topics are created if a movement
        topic with the same title already exists.
        """
        # Create an initial movement topic
        MovementTopic.objects.create(
            title="Outreach Techniques",
            content="Strategies for outreach.",
            author=self.profile,
        )

        # Call the function with a movement topic that already exists
        populate_movement_topics(self.predefined_movement_topics)

        # Check that only one movement topic with the title "Outreach Techniques" exists
        self.assertEqual(
            MovementTopic.objects.filter(title="Outreach Techniques").count(),
            1,
        )

    def test_first_profile_is_set_as_author_for_movements(self):
        """
        Test that the first profile in the database is set as the author for all created movements.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_movements(self.predefined_movements)

        # Check that the first profile is used as the author for all movements
        for movement in Movement.objects.all():
            self.assertEqual(movement.author, self.profile)

    def test_first_profile_is_set_as_author_for_movement_topics(self):
        """
        Test that the first profile in the database is set as the author
        for all created movement topics.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="anotheruser@example.com",
            password="password",
        )

        # Call the function
        populate_movement_topics(self.predefined_movement_topics)

        # Check that the first profile is used as the author for all movement topics
        for movement_topic in MovementTopic.objects.all():
            self.assertEqual(movement_topic.author, self.profile)
