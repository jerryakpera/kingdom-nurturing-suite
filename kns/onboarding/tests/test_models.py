import pytest
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from kns.custom_user.models import User
from kns.onboarding.models import (
    ProfileCompletion,
    ProfileCompletionTask,
    ProfileOnboarding,
)


class TestProfileOnboardingModel(TestCase):
    def setUp(self):
        """
        Setup method to create a User and Profile instance linked to it.
        Also initializes onboarding steps in settings for the tests.
        """
        self.user = User.objects.create_user(
            email="test.user@example.com",
            password="password123",
        )
        self.profile = self.user.profile
        self.profile.role = "leader"
        self.profile.save()

        self.onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
            current_step=1,
        )

        # Mock onboarding steps in settings
        settings.ONBOARDING_STEPS = {
            "profile": {
                "name": "Profile details",
                "template_name": "onboarding/profile.html",
            },
            "involvement": {
                "name": "Involvement preferences",
                "template_name": "onboarding/involvement.html",
            },
            "group": {
                "name": "Group registration",
                "template_name": "onboarding/group.html",
            },
            "agree": {
                "name": "Terms and Conditions",
                "template_name": "onboarding/agree.html",
            },
        }

    def tearDown(self):
        """
        Clear cache after each test.
        """
        cache.clear()

    def test_back_method(self):
        """
        Test that the `back` method correctly decreases the current step,
        ensuring it doesn't go below step 1.
        """
        self.onboarding.current_step = 2
        self.onboarding.save()

        self.onboarding.back()
        self.assertEqual(self.onboarding.current_step, 1)

        self.onboarding.back()  # Step should not go below 1
        self.assertEqual(self.onboarding.current_step, 1)

    def test_next_method(self):
        """
        Test that the `next` method correctly increases the current step,
        ensuring it doesn't exceed the number of available steps.
        """
        self.onboarding.next(self.profile)
        self.assertEqual(self.onboarding.current_step, 2)

        # There are 4 steps for a leader
        self.onboarding.current_step = 4
        self.onboarding.save()

        # Should not go beyond step 4
        self.onboarding.next(self.profile)
        self.assertEqual(self.onboarding.current_step, 4)

    def test_get_onboarding_steps_list(self):
        """
        Test that the `get_onboarding_steps_list` returns the correct list
        of steps based on the profile's role.
        """

        steps = self.onboarding.get_onboarding_steps_list(self.profile)

        # Leader should have 4 steps
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[0]["name"], "Profile details")
        self.assertEqual(
            steps[3]["name"],
            "Terms and Conditions",
        )

        # Change role to regular member and check step list
        self.profile.role = "member"
        self.profile.save()

        # Clear cache to ensure we get the correct steps for the new role
        cache.delete(f"onboarding_steps_{self.profile.id}")

        steps = self.onboarding.get_onboarding_steps_list(self.profile)

        self.assertEqual(len(steps), 3)  # Regular member should have 3 steps

    def test_get_current_step(self):
        """
        Test that `get_current_step` returns the correct current step
        based on the profile's onboarding progress.
        """
        current_step = self.onboarding.get_current_step(self.profile)

        self.assertEqual(
            current_step["name"],
            "Profile details",
        )

        self.onboarding.current_step = 2
        self.onboarding.save()

        current_step = self.onboarding.get_current_step(self.profile)

        self.assertEqual(
            current_step["name"],
            "Involvement preferences",
        )

    def test_is_last_step(self):
        """
        Test that `is_last_step` correctly identifies if the current step is the last step.
        """
        self.onboarding.current_step = 5
        self.onboarding.save()

        self.assertTrue(self.onboarding.is_last_step(self.profile))

        self.onboarding.current_step = 3
        self.onboarding.save()

        self.assertFalse(self.onboarding.is_last_step(self.profile))


class TestProfileCompletionTaskModel(TestCase):
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

    def test_profile_completion_task_creation(self):
        """
        Test that a ProfileCompletionTask instance can be created and is properly saved.
        """
        task = ProfileCompletionTask.objects.create(
            profile=self.profile,
            task_name="complete_profile",
            description="Complete all required fields in the profile.",
        )

        self.assertEqual(
            task.profile,
            self.profile,
        )
        self.assertEqual(
            task.task_name,
            "complete_profile",
        )
        self.assertEqual(
            task.description,
            "Complete all required fields in the profile.",
        )
        self.assertFalse(task.is_complete)

    def test_profile_completion_task_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        task = ProfileCompletionTask.objects.create(
            profile=self.profile,
            task_name="complete_profile",
            description="Complete all required fields in the profile.",
        )

        self.assertEqual(str(task), "complete_profile for Jane Doe")

    def test_mark_task_complete(self):
        """
        Test that the mark_complete method works correctly and updates
        the task status and completed_at field.
        """
        task = ProfileCompletionTask.objects.create(
            profile=self.profile,
            task_name="complete_profile",
            description="Complete all required fields in the profile.",
        )

        task.mark_complete()

        self.assertTrue(task.is_complete)
        self.assertIsNotNone(task.completed_at)
        self.assertLessEqual(task.completed_at, timezone.now())

    def test_profile_completion_task_unique_together(self):
        """
        Test that the combination of profile and task_name is unique in ProfileCompletionTask.
        """
        ProfileCompletionTask.objects.create(
            profile=self.profile,
            task_name="complete_profile",
            description="Complete all required fields in the profile.",
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileCompletionTask.objects.create(
                profile=self.profile,
                task_name="complete_profile",
                description="Duplicate task for the same profile.",
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_profile_completion_task_incomplete(self):
        """
        Test that a task is incomplete by default.
        """
        task = ProfileCompletionTask.objects.create(
            profile=self.profile,
            task_name="register_group",
            description="Register a new group.",
        )

        self.assertFalse(task.is_complete)
        self.assertIsNone(task.completed_at)


class TestProfileCompletionModel(TestCase):
    def setUp(self):
        """
        Setup method to create a User and Profile instance linked to it.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.profile.first_name = "John"
        self.profile.last_name = "Doe"

        self.profile.save()

        self.profile_completion = ProfileCompletion.objects.create(
            profile=self.profile,
        )

        # Create sample tasks
        self.tasks = [
            ProfileCompletionTask.objects.create(
                profile=self.profile,
                task_name="complete_profile",
                description="Complete your.",
            ),
            ProfileCompletionTask.objects.create(
                profile=self.profile,
                task_name="register_group",
                description="Register a new group.",
            ),
            ProfileCompletionTask.objects.create(
                profile=self.profile,
                task_name="register_first_member",
                description="Register the first member in the group.",
            ),
            ProfileCompletionTask.objects.create(
                profile=self.profile,
                task_name="add_vocations_skills",
                description="Add vocations and skills to the profile.",
            ),
        ]

    def test_is_profile_complete(self):
        """
        Test that `is_profile_complete` returns the correct status based on task completion.
        """
        self.assertFalse(self.profile_completion.is_profile_complete)

        # Mark all tasks as complete
        for task in self.tasks:
            task.mark_complete()

        self.assertTrue(self.profile_completion.is_profile_complete)

    def test_remaining_tasks(self):
        """
        Test that `remaining_tasks` returns incomplete tasks.
        """
        remaining = self.profile_completion.remaining_tasks()
        self.assertEqual(len(remaining), 4)

        # Mark all tasks as complete
        for task in self.tasks:
            task.mark_complete()

        remaining = self.profile_completion.remaining_tasks()
        self.assertEqual(len(remaining), 0)

    def test_completed_tasks(self):
        """
        Test that `completed_tasks` returns completed tasks.
        """
        completed = self.profile_completion.completed_tasks()
        self.assertEqual(len(completed), 0)

        # Mark all tasks as complete
        for task in self.tasks:
            task.mark_complete()

        completed = self.profile_completion.completed_tasks()
        self.assertEqual(len(completed), 4)

    def test_total_tasks(self):
        """
        Test that `total_tasks` returns the correct number of tasks.
        """
        self.assertEqual(self.profile_completion.total_tasks(), 4)

    def test_completed_task_count(self):
        """
        Test that `completed_task_count` returns the correct number of completed tasks.
        """
        self.assertEqual(self.profile_completion.completed_task_count(), 0)

        # Mark all tasks as complete
        for task in self.tasks:
            task.mark_complete()

        self.assertEqual(self.profile_completion.completed_task_count(), 4)

    def test_profile_completion_str_method(self):
        """
        Test that the `__str__` method returns the correct string representation.
        """
        self.assertEqual(
            str(self.profile_completion),
            f"Profile completion for {self.profile.get_full_name()}",
        )

    def test_profile_completion_unique(self):
        """
        Test that the combination of profile is unique in ProfileCompletion.
        """
        with pytest.raises(IntegrityError) as excinfo:
            ProfileCompletion.objects.create(
                profile=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_completion_percentage(self):
        """
        Test that `completion_percentage` returns the correct percentage of tasks completed.
        """
        # Scenario 1: No tasks completed
        self.assertEqual(
            self.profile_completion.completion_percentage(),
            0,
        )

        # Scenario 2: Some tasks completed
        # Assuming you start with 5 tasks and complete 2 of them
        tasks_to_complete = self.tasks[:2]  # Taking the first 2 tasks
        for task in tasks_to_complete:
            task.mark_complete()

        self.assertEqual(
            self.profile_completion.completion_percentage(),
            int((2 / len(self.tasks)) * 100),
        )

        # Scenario 3: All tasks completed
        for task in self.tasks:
            task.mark_complete()

        self.assertEqual(
            self.profile_completion.completion_percentage(),
            100,
        )

        # Scenario 4: No tasks
        # Remove all tasks and reset ProfileCompletion
        ProfileCompletionTask.objects.all().delete()
        self.profile_completion.delete()

        # Recreate ProfileCompletion instance with no tasks
        self.profile_completion = ProfileCompletion.objects.create(
            profile=self.profile,
        )

        self.assertEqual(
            self.profile_completion.completion_percentage(),
            100,
        )
