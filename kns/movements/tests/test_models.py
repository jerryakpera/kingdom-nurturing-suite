import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from kns.custom_user.models import User
from kns.movements.models import (
    Movement,
    MovementSyllabusItem,
    MovementTopic,
    ProfileMovement,
)
from kns.profiles.models import Profile


class TestMovementModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

    def test_movement_creation(self):
        """
        Test that a Movement instance can be created and is properly saved.
        """
        movement = Movement.objects.create(
            title="Disciple Making Movement",
            content="<p>Description of DMM</p>",
            author=self.profile,
            prayer_movement=True,
        )

        self.assertEqual(movement.title, "Disciple Making Movement")
        self.assertTrue(movement.prayer_movement)
        self.assertEqual(movement.content, "<p>Description of DMM</p>")

    def test_movement_slug_unique(self):
        """
        Test that the slug field on the Movement model is unique.
        """
        Movement.objects.create(
            title="Movement A",
            content="<p>Content for movement A</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Movement.objects.create(
                title="Movement A",
                content="<p>Duplicate movement A</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_movement_str_method(self):
        """
        Test that the __str__ method returns the title of the movement.
        """
        movement = Movement.objects.create(
            title="Disciple Making Movement",
            content="<p>Description of DMM</p>",
            author=self.profile,
        )

        self.assertEqual(str(movement), "Disciple Making Movement")


class TestMovementTopicModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

    def test_movement_topic_creation(self):
        """
        Test that a MovementTopic instance can be created and is properly saved.
        """
        topic = MovementTopic.objects.create(
            title="Evangelism",
            content="<p>Details about evangelism</p>",
            author=self.profile,
        )

        self.assertEqual(topic.title, "Evangelism")
        self.assertEqual(topic.content, "<p>Details about evangelism</p>")

    def test_movement_topic_slug_unique(self):
        """
        Test that the slug field on the MovementTopic model is unique.
        """
        MovementTopic.objects.create(
            title="Church Planting",
            content="<p>Church planting content</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MovementTopic.objects.create(
                title="Church Planting",
                content="<p>Duplicate topic</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_movement_topic_str_method(self):
        """
        Test that the __str__ method returns the title of the movement topic.
        """
        topic = MovementTopic.objects.create(
            title="Evangelism",
            content="<p>Details about evangelism</p>",
            author=self.profile,
        )

        self.assertEqual(str(topic), "Evangelism")


class TestProfileMovementModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile and Movement instances.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.movement = Movement.objects.create(
            title="Disciple Making Movement",
            content="<p>Description of DMM</p>",
            author=self.profile,
        )

    def test_profile_movement_creation(self):
        """
        Test that a ProfileMovement instance can be created and is properly saved.
        """
        profile_movement = ProfileMovement.objects.create(
            profile=self.profile,
            movement=self.movement,
            comprehension=2,  # Intermediate
        )

        self.assertEqual(profile_movement.profile, self.profile)
        self.assertEqual(profile_movement.movement, self.movement)
        self.assertEqual(profile_movement.comprehension, 2)

    def test_profile_movement_unique_together(self):
        """
        Test that the combination of profile and movement is unique in ProfileMovement.
        """
        ProfileMovement.objects.create(
            profile=self.profile,
            movement=self.movement,
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileMovement.objects.create(
                profile=self.profile,
                movement=self.movement,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_profile_movement_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        profile_movement = ProfileMovement.objects.create(
            profile=self.profile,
            movement=self.movement,
        )

        self.assertEqual(str(profile_movement), "Jane Doe")

    def test_profile_movement_increment_comprehension(self):
        """
        Test that the comprehension level is incremented properly.
        """
        profile_movement = ProfileMovement.objects.create(
            profile=self.profile,
            movement=self.movement,
            comprehension=1,  # Beginner
        )

        profile_movement.increment_comprehension()

        self.assertEqual(
            profile_movement.comprehension, 2
        )  # Should now be Intermediate

        profile_movement.increment_comprehension()

        self.assertEqual(profile_movement.comprehension, 3)  # Should now be Expert

        # No increment beyond Expert
        profile_movement.increment_comprehension()

        self.assertEqual(profile_movement.comprehension, 3)  # Still Expert


class TestMovementSyllabusItemModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile, Movement, and MovementTopic instances.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.movement = Movement.objects.create(
            title="Disciple Making Movement",
            content="<p>Description of DMM</p>",
            author=self.profile,
        )

        self.topic = MovementTopic.objects.create(
            title="Evangelism",
            content="<p>Details about evangelism</p>",
            author=self.profile,
        )

    def test_movement_syllabus_item_creation(self):
        """
        Test that a MovementSyllabusItem instance can be created and is properly saved.
        """
        syllabus_item = MovementSyllabusItem.objects.create(
            movement=self.movement,
            topic=self.topic,
        )

        self.assertEqual(syllabus_item.movement, self.movement)
        self.assertEqual(syllabus_item.topic, self.topic)

    def test_movement_syllabus_item_unique_together(self):
        """
        Test that the combination of movement and topic is unique in MovementSyllabusItem.
        """
        MovementSyllabusItem.objects.create(
            movement=self.movement,
            topic=self.topic,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MovementSyllabusItem.objects.create(
                movement=self.movement,
                topic=self.topic,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_movement_syllabus_item_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        syllabus_item = MovementSyllabusItem.objects.create(
            movement=self.movement,
            topic=self.topic,
        )

        self.assertEqual(
            str(syllabus_item),
            "Evangelism in Disciple Making Movement's syllabus",
        )
