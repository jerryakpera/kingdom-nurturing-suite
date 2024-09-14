from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from kns.custom_user.models import User
from kns.mentorships.models import (
    MentorEndorsement,
    Mentorship,
    MentorshipArea,
    MentorshipAreaMentorshipGoal,
    MentorshipFeedback,
    MentorshipGoal,
    MentorshipMentorshipGoal,
    ProfileMentorshipArea,
)


class TestMentorshipAreaModel(TestCase):
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

    def test_mentorship_area_creation(self):
        """
        Test that a MentorshipArea instance can be created and is properly saved.
        """
        mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        self.assertEqual(mentorship_area.title, "Software Engineering")
        self.assertEqual(
            mentorship_area.content, "<p>Advanced concepts in software development.</p>"
        )

    def test_mentorship_area_slug_unique(self):
        """
        Test that the slug field on the MentorshipArea model is unique.
        """
        MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MentorshipArea.objects.create(
                title="Software Engineering",
                content="<p>Different content.</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_mentorship_area_str_method(self):
        """
        Test that the __str__ method returns the title of the mentorship area.
        """
        mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        self.assertEqual(str(mentorship_area), "Software Engineering")


class TestMentorshipGoalModel(TestCase):
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

    def test_mentorship_goal_creation(self):
        """
        Test that a MentorshipGoal instance can be created and is properly saved.
        """
        mentorship_goal = MentorshipGoal.objects.create(
            title="Career Development",
            content="<p>Goals for career growth and advancement.</p>",
            author=self.profile,
            type="primary",
        )

        self.assertEqual(mentorship_goal.title, "Career Development")
        self.assertEqual(
            mentorship_goal.content,
            "<p>Goals for career growth and advancement.</p>",
        )
        self.assertEqual(mentorship_goal.type, "primary")

    def test_mentorship_goal_slug_unique(self):
        """
        Test that the slug field on the MentorshipGoal model is unique.
        """
        MentorshipGoal.objects.create(
            title="Career Development",
            content="<p>Goals for career growth and advancement.</p>",
            author=self.profile,
            type="primary",
        )

        with pytest.raises(IntegrityError) as excinfo:
            MentorshipGoal.objects.create(
                title="Career Development",
                content="<p>Different content.</p>",
                author=self.profile,
                type="secondary",
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_mentorship_goal_str_method(self):
        """
        Test that the __str__ method returns the title of the mentorship goal.
        """
        mentorship_goal = MentorshipGoal.objects.create(
            title="Career Development",
            content="<p>Goals for career growth and advancement.</p>",
            author=self.profile,
            type="primary",
        )

        self.assertEqual(str(mentorship_goal), "Career Development")


class TestMentorshipAreaMentorshipGoalModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user,
        and instances of MentorshipArea and MentorshipGoal.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

        # Create MentorshipArea and MentorshipGoal instances
        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        self.mentorship_goal = MentorshipGoal.objects.create(
            title="Advanced Programming",
            content="<p>Learning advanced programming techniques.</p>",
            author=self.profile,
            type="primary",
        )

    def test_mentorship_area_mentorship_goal_creation(self):
        """
        Test that a MentorshipAreaMentorshipGoal instance can be created
        and is properly saved.
        """
        relationship = MentorshipAreaMentorshipGoal.objects.create(
            mentorship_area=self.mentorship_area,
            mentorship_goal=self.mentorship_goal,
        )

        self.assertEqual(
            relationship.mentorship_area,
            self.mentorship_area,
        )
        self.assertEqual(
            relationship.mentorship_goal,
            self.mentorship_goal,
        )

    def test_mentorship_area_mentorship_goal_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the MentorshipAreaMentorshipGoal instance.
        """
        relationship = MentorshipAreaMentorshipGoal.objects.create(
            mentorship_area=self.mentorship_area,
            mentorship_goal=self.mentorship_goal,
        )

        expected_str = f"{self.mentorship_area.title} ({self.mentorship_goal.title})"
        self.assertEqual(str(relationship), expected_str)

    def test_unique_together_constraint(self):
        """
        Test that the unique_together constraint on mentorship_area and
        mentorship_goal is enforced.
        """
        MentorshipAreaMentorshipGoal.objects.create(
            mentorship_area=self.mentorship_area,
            mentorship_goal=self.mentorship_goal,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MentorshipAreaMentorshipGoal.objects.create(
                mentorship_area=self.mentorship_area,
                mentorship_goal=self.mentorship_goal,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)


class TestProfileMentorshipAreaModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance and a MentorshipArea instance.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"
        self.profile.save()

        # Create MentorshipArea instance
        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

    def test_profile_mentorship_area_creation(self):
        """
        Test that a ProfileMentorshipArea instance can be created
        and is properly saved.
        """
        relationship = ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area,
        )

        self.assertEqual(relationship.profile, self.profile)
        self.assertEqual(
            relationship.mentorship_area,
            self.mentorship_area,
        )

    def test_profile_mentorship_area_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the ProfileMentorshipArea instance.
        """
        relationship = ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area,
        )

        expected_str = f"{self.profile.get_full_name()} {self.mentorship_area.title}"
        self.assertEqual(str(relationship), expected_str)

    def test_unique_together_constraint(self):
        """
        Test that the unique_together constraint on profile and
        mentorship_area is enforced.
        """
        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area,
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileMentorshipArea.objects.create(
                profile=self.profile,
                mentorship_area=self.mentorship_area,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)


class TestMentorshipModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile instances and a MentorshipArea instance.
        """
        self.user1 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="mentee@example.com",
            password="password",
        )

        self.mentor = self.user1.profile
        self.mentor.first_name = "Mentor"
        self.mentor.last_name = "One"
        self.mentor.save()

        self.mentee = self.user2.profile
        self.mentee.first_name = "Mentee"
        self.mentee.last_name = "Two"
        self.mentee.save()

        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.mentor,
        )

    def test_mentorship_creation(self):
        """
        Test that a Mentorship instance can be created and is properly saved.
        """
        mentorship = Mentorship.objects.create(
            mentorship_area=self.mentorship_area,
            mentor=self.mentor,
            mentee=self.mentee,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(weeks=4),
            duration=4,
            mentor_approval_required=True,
            group_leader_approval_required=False,
            author=self.mentor,
            status="active",
        )

        self.assertEqual(
            mentorship.mentorship_area,
            self.mentorship_area,
        )
        self.assertEqual(mentorship.mentor, self.mentor)
        self.assertEqual(mentorship.mentee, self.mentee)
        self.assertEqual(mentorship.duration, 4)
        self.assertEqual(mentorship.status, "active")

    def test_mentorship_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the Mentorship instance.
        """
        mentorship = Mentorship.objects.create(
            mentorship_area=self.mentorship_area,
            mentor=self.mentor,
            mentee=self.mentee,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(weeks=4),
            duration=4,
            mentor_approval_required=True,
            group_leader_approval_required=False,
            author=self.mentor,
            status="active",
        )

        expected_str = f"{self.mentor.get_full_name()} -> {self.mentee.get_full_name()}"
        self.assertEqual(str(mentorship), expected_str)


class TestMentorshipMentorshipGoalModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile instances, a MentorshipArea instance, and
        Mentorship and MentorshipGoal instances.
        """
        self.user1 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="mentee@example.com",
            password="password",
        )

        self.mentor = self.user1.profile
        self.mentor.first_name = "Mentor"
        self.mentor.last_name = "One"
        self.mentor.save()

        self.mentee = self.user2.profile
        self.mentee.first_name = "Mentee"
        self.mentee.last_name = "Two"
        self.mentee.save()

        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.mentor,
        )

        self.mentorship = Mentorship.objects.create(
            mentorship_area=self.mentorship_area,
            mentor=self.mentor,
            mentee=self.mentee,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(weeks=4),
            duration=4,
            mentor_approval_required=True,
            group_leader_approval_required=False,
            author=self.mentor,
            status="active",
        )

        self.mentorship_goal = MentorshipGoal.objects.create(
            title="Advanced Programming",
            content="<p>Learning advanced programming techniques.</p>",
            author=self.mentor,
            type="primary",
        )

    def test_mentorship_mentorship_goal_creation(self):
        """
        Test that a MentorshipMentorshipGoal instance can be created
        and is properly saved.
        """
        relationship = MentorshipMentorshipGoal.objects.create(
            mentorship=self.mentorship,
            mentorship_goal=self.mentorship_goal,
        )

        self.assertEqual(relationship.mentorship, self.mentorship)
        self.assertEqual(relationship.mentorship_goal, self.mentorship_goal)

    def test_mentorship_mentorship_goal_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the MentorshipMentorshipGoal instance.
        """
        relationship = MentorshipMentorshipGoal.objects.create(
            mentorship=self.mentorship,
            mentorship_goal=self.mentorship_goal,
        )

        expected_str = (
            f"{self.mentorship_goal.title} - {self.mentorship.mentor.get_full_name()} "
            f"mentoring {self.mentorship.mentee.get_full_name()}"
        )

        self.assertEqual(str(relationship), expected_str)

    def test_unique_together_constraint(self):
        """
        Test that the unique_together constraint on mentorship and
        mentorship_goal is enforced.
        """
        MentorshipMentorshipGoal.objects.create(
            mentorship=self.mentorship,
            mentorship_goal=self.mentorship_goal,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MentorshipMentorshipGoal.objects.create(
                mentorship=self.mentorship,
                mentorship_goal=self.mentorship_goal,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)


class TestMentorEndorsementModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile instances for the mentor and endorser.
        """
        self.user1 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="endorser@example.com",
            password="password",
        )

        self.mentor = self.user1.profile
        self.mentor.first_name = "Mentor"
        self.mentor.last_name = "One"
        self.mentor.save()

        self.endorser = self.user2.profile
        self.endorser.first_name = "Endorser"
        self.endorser.last_name = "Two"
        self.endorser.save()

    def test_mentor_endorsement_creation(self):
        """
        Test that a MentorEndorsement instance can be created and is properly saved.
        """
        endorsement = MentorEndorsement.objects.create(
            mentor=self.mentor,
            endorser=self.endorser,
            message="Great mentor!",
        )

        self.assertEqual(endorsement.mentor, self.mentor)
        self.assertEqual(endorsement.endorser, self.endorser)
        self.assertEqual(endorsement.message, "Great mentor!")

    def test_mentor_endorsement_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the MentorEndorsement instance.
        """
        endorsement = MentorEndorsement.objects.create(
            mentor=self.mentor,
            endorser=self.endorser,
            message="Great mentor!",
        )

        expected_str = (
            f"{self.endorser.get_full_name()} endorsed {self.mentor.get_full_name()}"
        )
        self.assertEqual(str(endorsement), expected_str)

    def test_unique_together_constraint(self):
        """
        Test that the unique_together constraint on mentor and endorser is enforced.
        """
        MentorEndorsement.objects.create(
            mentor=self.mentor,
            endorser=self.endorser,
            message="Great mentor!",
        )

        with self.assertRaises(IntegrityError):
            MentorEndorsement.objects.create(
                mentor=self.mentor,
                endorser=self.endorser,
                message="Another endorsement message.",
            )


class TestMentorshipFeedbackModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile instances, a Mentorship instance, and
        a MentorshipFeedback instance.
        """
        self.user1 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="mentee@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="author@example.com",
            password="password",
        )

        self.mentor = self.user1.profile
        self.mentor.first_name = "Mentor"
        self.mentor.last_name = "One"
        self.mentor.save()

        self.mentee = self.user2.profile
        self.mentee.first_name = "Mentee"
        self.mentee.last_name = "Two"
        self.mentee.save()

        self.author = self.user3.profile
        self.author.first_name = "Author"
        self.author.last_name = "Three"
        self.author.save()

        self.mentorship = Mentorship.objects.create(
            mentorship_area=MentorshipArea.objects.create(
                title="Software Engineering",
                content="<p>Advanced concepts in software development.</p>",
                author=self.mentor,
            ),
            mentor=self.mentor,
            mentee=self.mentee,
            start_date=timezone.now().date(),
            expected_end_date=timezone.now().date() + timedelta(weeks=4),
            duration=4,
            mentor_approval_required=True,
            group_leader_approval_required=False,
            author=self.mentor,
            status="active",
        )

    def test_mentorship_feedback_creation(self):
        """
        Test that a MentorshipFeedback instance can be created and is properly saved.
        """
        feedback = MentorshipFeedback.objects.create(
            mentorship=self.mentorship,
            author=self.author,
            comments="The mentorship was very helpful.",
            rating=5,
        )

        self.assertEqual(feedback.mentorship, self.mentorship)
        self.assertEqual(feedback.author, self.author)
        self.assertEqual(feedback.comments, "The mentorship was very helpful.")
        self.assertEqual(feedback.rating, 5)

    def test_mentorship_feedback_str_method(self):
        """
        Test that the __str__ method returns the correct string representation
        of the MentorshipFeedback instance.
        """
        feedback = MentorshipFeedback.objects.create(
            mentorship=self.mentorship,
            author=self.author,
            comments="The mentorship was very helpful.",
            rating=5,
        )

        expected_str = f"Feedback for {self.mentorship}"
        self.assertEqual(str(feedback), expected_str)

    def test_feedback_rating_constraints(self):
        """
        Test that the rating field has proper constraints (e.g., min and max values).
        """
        # Valid rating
        feedback = MentorshipFeedback.objects.create(
            mentorship=self.mentorship,
            author=self.author,
            comments="The mentorship was excellent.",
            rating=5,
        )
        self.assertEqual(feedback.rating, 5)

        # Invalid rating (should raise ValidationError)
        invalid_feedback = MentorshipFeedback(
            mentorship=self.mentorship,
            author=self.author,
            comments="Invalid rating test.",
            rating=10,  # Assuming the rating should be between 1 and 5
        )
        with self.assertRaises(ValidationError):
            invalid_feedback.full_clean()  # This should raise a ValidationError
