from datetime import datetime, timedelta
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
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
from kns.activities.tests.factories import (
    ActivityFacilitatorFactory,
    ActivityFacilitatorInvitationFactory,
    ActivityFactory,
    ActivityFeedbackFactory,
    ActivityRegistrationFactory,
)
from kns.events.models import Event
from kns.events.tests.factories import EventFactory
from kns.profiles.models import User


class TestActivityFactory(TestCase):
    def setUp(self):
        """
        Set up a test user and log them in. This user will be the author
        of activities created by the factory.
        """
        self.client = self.client_class()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        # Creating the profile for the user
        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

    def test_factory(self):
        """
        Test if the ActivityFactory produces a valid instance of Activity.
        """
        activity = ActivityFactory()

        self.assertIsNotNone(activity)
        self.assertNotEqual(activity.title, "")
        self.assertNotEqual(activity.description, "")
        self.assertIsNotNone(activity.author)
        self.assertIsNotNone(activity.start_date)
        self.assertIsNotNone(activity.event)
        self.assertIsNotNone(activity.start_time)
        self.assertIn(
            activity.activity_type,
            [
                "skill_training",
                "movement_training",
                "community_service",
                "prayer_movement",
            ],
        )

    def test_slug_generation(self):
        """
        Test if the slug is generated correctly based on the title.
        """
        activity = ActivityFactory(
            title="Sample Activity Title",
        )
        self.assertEqual(
            activity.slug,
            slugify("Sample Activity Title"),
        )

    def test_str_method(self):
        """
        Test if the __str__ method returns the correct string representation of the activity.
        """
        activity = ActivityFactory(
            title="Community Service",
            start_date=datetime.strptime("2024-10-20", "%Y-%m-%d"),
        )
        self.assertEqual(str(activity), "Community Service")  # Based on __str__ method

    def test_scope(self):
        """
        Test that the scope is correctly set in the factory.
        """
        activity = ActivityFactory(scope="comprehensive")
        self.assertEqual(activity.scope, "comprehensive")

        activity = ActivityFactory(scope="abridged")
        self.assertEqual(activity.scope, "abridged")

    def test_end_date_after_start_date(self):
        """
        Test that the end date is always after the start date.
        """
        activity = ActivityFactory()
        self.assertGreaterEqual(activity.end_date, activity.start_date)

    def test_event_relation(self):
        """
        Test that the event relation is correctly set.
        """
        activity = ActivityFactory()
        self.assertIsNotNone(activity.event)
        self.assertEqual(activity.event.__class__.__name__, "Event")


class TestActivityRegistrationFactory(TestCase):
    def setUp(self):
        """
        Set up a test user and log them in. This user will be associated
        with activity registrations created by the factory.
        """
        self.client = self.client_class()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        # Creating the profile for the user
        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        # Creating an activity for registration
        self.activity = ActivityFactory()

    def test_factory(self):
        """
        Test if the ActivityRegistrationFactory produces a valid instance of ActivityRegistration.
        """
        registration = ActivityRegistrationFactory(
            activity=self.activity, profile=self.profile
        )

        self.assertIsNotNone(registration)
        self.assertEqual(
            registration.activity.id,
            self.activity.id,
        )
        self.assertEqual(
            registration.profile.id,
            self.profile.id,
        )
        self.assertIn(
            registration.status,
            [choice[0] for choice in ActivityRegistration.STATUS_CHOICES],
        )
        self.assertNotEqual(registration.guest_name, "")
        self.assertNotEqual(registration.guest_email, "")
        self.assertIsNotNone(registration.confirmation_token)
        self.assertIsNotNone(registration.rejection_token)

    def test_str_method(self):
        """
        Test if the __str__ method returns the correct string representation
        of the registration.
        """
        registration = ActivityRegistrationFactory(
            activity=self.activity,
            profile=self.profile,
        )

        expected_str = (
            f"{self.profile.first_name} {self.profile.last_name}" f" - {self.activity}"
        )

        # Check if the string representation matches the expected format
        self.assertEqual(str(registration), expected_str)

    def test_activity_relation(self):
        """
        Test that the activity relation is correctly set.
        """
        registration = ActivityRegistrationFactory(
            activity=self.activity,
            profile=self.profile,
        )

        self.assertIsNotNone(registration.activity)
        self.assertEqual(registration.activity.id, self.activity.id)

    def test_profile_relation(self):
        """
        Test that the profile relation is correctly set.
        """
        registration = ActivityRegistrationFactory(
            activity=self.activity, profile=self.profile
        )

        self.assertIsNotNone(registration.profile)
        self.assertEqual(registration.profile.id, self.profile.id)

    def test_guest_registration(self):
        """
        Test that the registration can be a guest registration and is handled correctly.
        """
        registration = ActivityRegistrationFactory(
            activity=self.activity,
            profile=self.profile,
            is_guest=True,
        )

        self.assertTrue(registration.is_guest)
        self.assertIsNotNone(registration.guest_name)
        self.assertIsNotNone(registration.guest_email)

    def test_status_choices(self):
        """
        Test that the status is set correctly from the STATUS_CHOICES.
        """
        for status in [choice[0] for choice in ActivityRegistration.STATUS_CHOICES]:
            registration = ActivityRegistrationFactory(
                activity=self.activity,
                profile=self.profile,
                status=status,
            )

            self.assertEqual(registration.status, status)


class TestActivityFacilitatorFactory(TestCase):
    def setUp(self):
        """
        Set up a test user and log them in. This user will be the facilitator
        of activities created by the factory.
        """
        self.client = self.client_class()
        self.user = User.objects.create_user(
            email="facilitator@example.com",
            password="password123",
        )
        self.client.login(
            email="facilitator@example.com",
            password="password123",
        )

        # Creating the profile for the facilitator
        self.profile = self.user.profile
        self.profile.first_name = "Facilitator"
        self.profile.last_name = "User"
        self.profile.save()

    def test_factory(self):
        """
        Test if the ActivityFacilitatorFactory produces a valid instance of ActivityFacilitator.
        """
        facilitator = ActivityFacilitatorFactory()

        self.assertIsNotNone(facilitator)
        self.assertIsNotNone(facilitator.activity)
        self.assertIsNotNone(facilitator.facilitator)
        self.assertEqual(facilitator.activity.__class__.__name__, "Activity")
        self.assertEqual(facilitator.facilitator.__class__.__name__, "Profile")

    def test_str_method(self):
        """
        Test if the __str__ method returns the correct string representation of the facilitator.
        """
        facilitator = ActivityFacilitatorFactory(
            activity=ActivityFactory(title="Sample Activity"),
            facilitator=self.profile,
        )
        self.assertEqual(str(facilitator), "Facilitator User for Sample Activity")

    def test_activity_relation(self):
        """
        Test that the activity relation is correctly set.
        """
        activity = ActivityFactory()
        facilitator = ActivityFacilitatorFactory(activity=activity)

        self.assertIsNotNone(facilitator.activity)
        self.assertEqual(facilitator.activity.id, activity.id)

    def test_facilitator_relation(self):
        """
        Test that the facilitator relation is correctly set.
        """
        facilitator = ActivityFacilitatorFactory(facilitator=self.profile)

        self.assertIsNotNone(facilitator.facilitator)
        self.assertEqual(facilitator.facilitator.id, self.profile.id)


class TestActivityFacilitatorInvitationFactory(TestCase):
    def setUp(self):
        """
        Set up a test user and log them in. This user will be used as the
        facilitator for the invitation.
        """
        self.client = self.client_class()
        self.user = User.objects.create_user(
            email="facilitator_invite@example.com",
            password="password123",
        )
        self.client.login(
            email="facilitator_invite@example.com",
            password="password123",
        )

        # Creating the profile for the facilitator
        self.profile = self.user.profile
        self.profile.first_name = "Facilitator"
        self.profile.last_name = "Invitee"
        self.profile.save()

        # Creating an activity for the facilitator
        self.activity = ActivityFactory()

    def test_factory(self):
        """
        Test if the ActivityFacilitatorInvitationFactory produces a valid
        instance of ActivityFacilitatorInvitation.
        """
        invitation = ActivityFacilitatorInvitationFactory(
            activity=self.activity,
            facilitator=self.profile,
            status="Pending",
        )

        self.assertIsNotNone(invitation)
        self.assertIsNotNone(invitation.activity)
        self.assertIsNotNone(invitation.facilitator)
        self.assertNotEqual(invitation.invitation_message, "")
        self.assertIn(
            invitation.status,
            [choice[0] for choice in ActivityFacilitatorInvitation.STATUS_CHOICES],
        )

    def test_str_method(self):
        """
        Test if the __str__ method returns the correct string representation
        of the facilitator invitation.
        """
        invitation = ActivityFacilitatorInvitationFactory(
            activity=self.activity,
            facilitator=self.profile,
        )

        expected_str = (
            f"Invitation for {self.profile.get_full_name()} to "
            f"facilitate {self.activity.title}"
        )

        self.assertEqual(str(invitation), expected_str)

    def test_activity_relation(self):
        """
        Test that the activity relation is correctly set.
        """
        invitation = ActivityFacilitatorInvitationFactory(
            activity=self.activity,
            facilitator=self.profile,
        )

        self.assertIsNotNone(invitation.activity)
        self.assertEqual(invitation.activity.id, self.activity.id)

    def test_facilitator_relation(self):
        """
        Test that the facilitator relation is correctly set.
        """
        invitation = ActivityFacilitatorInvitationFactory(
            activity=self.activity,
            facilitator=self.profile,
        )

        self.assertIsNotNone(invitation.facilitator)
        self.assertEqual(invitation.facilitator.id, self.profile.id)

    def test_status_choices(self):
        """
        Test that the status is set correctly from the STATUS_CHOICES.
        """
        for status in [
            choice[0] for choice in ActivityFacilitatorInvitation.STATUS_CHOICES
        ]:
            activity = ActivityFactory()

            invitation = ActivityFacilitatorInvitationFactory(
                activity=activity,
                facilitator=self.profile,
                status=status,
            )

            self.assertEqual(invitation.status, status)


class TestActivityFeedbackFactory(TestCase):
    def setUp(self):
        """
        Set up a test user and log them in. This user will be associated
        with feedback created by the factory.
        """
        self.client = self.client_class()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        # Creating the profile for the user
        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        # Creating an activity for feedback
        self.activity = ActivityFactory()

    def test_factory(self):
        """
        Test if the ActivityFeedbackFactory produces a valid instance of ActivityFeedback.
        """
        feedback = ActivityFeedbackFactory(
            activity=self.activity,
            profile=self.profile,
        )

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.activity.id, self.activity.id)
        self.assertEqual(feedback.profile.id, self.profile.id)
        self.assertIn(
            feedback.rating, [1, 2, 3, 4, 5]
        )  # Ensure rating is between 1 and 5
        self.assertIsNotNone(
            feedback.comment
        )  # Comment can be empty but should not be None

    def test_str_method(self):
        """
        Test if the __str__ method returns the correct string
        representation of the feedback.
        """
        feedback = ActivityFeedbackFactory(
            activity=self.activity,
            profile=self.profile,
            comment="Great activity!",
        )

        expected_str = (
            f"Feedback for {self.activity.title} by {self.profile.get_full_name()}"
        )
        self.assertEqual(str(feedback), expected_str)

    def test_activity_relation(self):
        """
        Test that the activity relation is correctly set.
        """
        feedback = ActivityFeedbackFactory(
            activity=self.activity,
            profile=self.profile,
        )

        self.assertIsNotNone(feedback.activity)
        self.assertEqual(feedback.activity.id, self.activity.id)

    def test_profile_relation(self):
        """
        Test that the profile relation is correctly set.
        """
        feedback = ActivityFeedbackFactory(
            activity=self.activity,
            profile=self.profile,
        )

        self.assertIsNotNone(feedback.profile)
        self.assertEqual(
            feedback.profile.id,
            self.profile.id,
        )

    def test_rating_validation(self):
        """
        Test that the rating is validated correctly between 1 and 5.
        """
        feedback = ActivityFeedbackFactory(
            activity=self.activity,
            profile=self.profile,
            rating=0,
        )

        with self.assertRaises(ValidationError):
            feedback.full_clean()

        feedback.rating = 6
        with self.assertRaises(ValidationError):
            feedback.full_clean()


class TestActivity(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to act as the activity author
        self.user = User.objects.create_user(
            email="organizer@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an event instance to link to the activity
        self.event = EventFactory(author=self.profile)

        # Create an activity instance using the factory
        self.activity = ActivityFactory(
            event=self.event,
            author=self.profile,
        )

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns the activity title.
        """
        activity = ActivityFactory(title="Sample Activity")
        self.assertEqual(str(activity), "Sample Activity")

    def test_slug_generation_on_save(self):
        """
        Test that a slug is generated from the title when saving the activity.
        """
        activity = Activity(
            title="Test Activity",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        activity.save()
        self.assertEqual(activity.slug, slugify(activity.title))

    def test_slug_uniqueness(self):
        """
        Test that slug uniqueness is enforced when saving multiple activities with the same title.
        """
        Activity.objects.create(
            title="Unique Title",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        # Attempt to create a second activity with the same title
        activity_with_duplicate_slug = Activity(
            title="Unique Title",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        with self.assertRaises(ValidationError):
            activity_with_duplicate_slug.full_clean()

    def test_end_date_validation(self):
        """
        Test that a ValidationError is raised if the end date is earlier than
        the start date.
        """
        activity = Activity(
            title="Activity with Invalid Dates",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timedelta(days=1),
            start_time=timezone.now().time(),
        )

        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_registration_is_open(self):
        """
        Test the `registration_is_open` method to ensure it correctly identifies
        if registration is open.
        """
        # Set up activity start date and event registration deadline
        self.activity.start_date = timezone.now().date() + timedelta(days=1)
        self.activity.event.registration_deadline_date = (
            timezone.now().date() + timedelta(days=2)
        )
        self.activity.save()
        self.assertTrue(self.activity.registration_is_open())

        # Set the registration deadline to today, registration should now be closed
        self.activity.event.registration_deadline_date = timezone.now().date()
        self.activity.save()
        self.assertFalse(self.activity.registration_is_open())

        # Set registration deadline to a past date, registration should be closed
        self.activity.event.registration_deadline_date = (
            timezone.now().date() - timedelta(days=1)
        )
        self.activity.save()
        self.assertFalse(self.activity.registration_is_open())

    def test_registration_is_open_no_deadline(self):
        """
        Test registration is open when there's no registration deadline set.
        """
        self.activity.start_date = timezone.now().date() + timedelta(days=1)
        self.activity.event.registration_deadline_date = None
        self.activity.save()
        self.assertTrue(self.activity.registration_is_open())

    def test_registration_is_open_event_started(self):
        """
        Test that registration is closed when the event has started.
        """
        # Set the event to have already started
        self.activity.start_date = timezone.now().date() - timedelta(days=1)
        self.activity.event.registration_deadline_date = (
            timezone.now().date() + timedelta(days=2)
        )
        self.activity.save()
        self.assertFalse(self.activity.registration_is_open())

    def test_is_upcoming(self):
        """
        Test that the is_upcoming method correctly identifies an upcoming activity.
        """
        self.activity.start_date = timezone.now().date() + timedelta(days=5)
        self.assertTrue(self.activity.is_upcoming())

        self.activity.start_date = timezone.now().date() - timedelta(days=2)
        self.assertFalse(self.activity.is_upcoming())

    def test_is_ongoing(self):
        """
        Test that the is_ongoing method correctly identifies an ongoing activity.
        """
        today = timezone.now().date()
        self.activity.start_date = today - timedelta(days=1)
        self.activity.end_date = today + timedelta(days=1)
        self.assertTrue(self.activity.is_ongoing())

        self.activity.start_date = today + timedelta(days=1)
        self.assertFalse(self.activity.is_ongoing())

    def test_is_past(self):
        """
        Test that the is_past method correctly identifies a past activity.
        """
        self.activity.end_date = timezone.now().date() - timedelta(days=1)
        self.assertTrue(self.activity.is_past())

        self.activity.end_date = timezone.now().date() + timedelta(days=1)
        self.assertFalse(self.activity.is_past())


class TestActivityRegistration(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to act as the registrant
        self.user = User.objects.create_user(
            email="registrant@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an activity instance to link to the registration
        self.activity = ActivityFactory()

        # Create an activity registration instance
        self.registration = ActivityRegistration.objects.create(
            activity=self.activity,
            profile=self.profile,
            status="Registered",
        )

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns 'registrant name - activity title'.
        """
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            profile=self.profile,
        )
        expected_str = f"{self.profile.get_full_name()} - {self.activity.title}"
        self.assertEqual(str(registration), expected_str)

    def test_guest_registration_str_method(self):
        """
        Test the __str__ method for guest registration to ensure it returns
        'guest name - activity title'.
        """
        guest_name = "Guest User"
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            guest_name=guest_name,
            guest_email="guest@example.com",
            is_guest=True,
        )
        expected_str = f"{guest_name} - {self.activity.title}"
        self.assertEqual(str(registration), expected_str)

    def test_registration_name_with_profile(self):
        """
        Test the `registration_name` property when the registration is profile-based.
        """
        self.assertEqual(
            self.registration.registration_name, self.profile.get_full_name()
        )

    def test_registration_name_with_guest(self):
        """
        Test the `registration_name` property when the registration is guest-based.
        """
        guest_name = "Guest User"
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            guest_name=guest_name,
            guest_email="guest@example.com",
            is_guest=True,
        )
        self.assertEqual(registration.registration_name, guest_name)

    def test_profile_registrations_queryset(self):
        """
        Test the `profile_registrations` method to ensure it returns only
        profile-based registrations.
        """
        # Create a guest registration
        ActivityRegistration.objects.create(
            activity=self.activity,
            guest_name="Guest User",
            guest_email="guest@example.com",
            is_guest=True,
        )

        profile_registrations = ActivityRegistration.profile_registrations()
        self.assertEqual(profile_registrations.count(), 1)
        self.assertEqual(profile_registrations.first().profile, self.profile)

    def test_confirmation_token_generated(self):
        """
        Test that the confirmation_token is generated when saving a registration.
        """
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            profile=self.profile,
        )
        self.assertIsNotNone(registration.confirmation_token)
        self.assertIsInstance(registration.confirmation_token, uuid4().__class__)

    def test_rejection_token_generated(self):
        """
        Test that the rejection_token is generated when saving a registration.
        """
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            profile=self.profile,
        )
        self.assertIsNotNone(registration.rejection_token)
        self.assertIsInstance(registration.rejection_token, uuid4().__class__)


class TestActivityAttendance(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to act as the registrant
        self.user = User.objects.create_user(
            email="registrant@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an activity instance
        self.activity = ActivityFactory()

        # Create an activity registration instance
        self.registration = ActivityRegistration.objects.create(
            activity=self.activity,
            profile=self.profile,
            status="Registered",
        )

        # Create an activity attendance instance
        self.attendance = ActivityAttendance.objects.create(
            registration=self.registration,
        )

    def test_str_method_with_profile(self):
        """
        Test the __str__ method when the attendance is profile-based.
        """

        expected_str = (
            f"Attendance for {self.registration.profile.user.username} "
            f"at {self.activity.title}"
        )

        self.assertEqual(
            str(self.attendance),
            expected_str,
        )

    def test_str_method_with_guest(self):
        """
        Test the __str__ method when the attendance is guest-based.
        """
        guest_name = "Guest User"
        guest_registration = ActivityRegistration.objects.create(
            activity=self.activity,
            guest_name=guest_name,
            guest_email="guest@example.com",
            is_guest=True,
        )

        attendance = ActivityAttendance.objects.create(
            registration=guest_registration,
        )

        expected_str = f"Attendance for {guest_name} at {self.activity.title}"
        self.assertEqual(str(attendance), expected_str)

    def test_check_in_time_is_none_initially(self):
        """
        Test that check_in_time is None initially.
        """
        self.assertIsNone(self.attendance.check_in_time)

    def test_set_check_in_time(self):
        """
        Test setting the check_in_time field.
        """
        check_in_time = timezone.now()
        self.attendance.check_in_time = check_in_time
        self.attendance.save()

        self.assertEqual(self.attendance.check_in_time, check_in_time)

    def test_attendance_for_non_existing_registration(self):
        """
        Test that creating an attendance record without a
        registration raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ActivityAttendance.objects.create(
                registration=None,
            )


class TestActivityFacilitator(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to act as the facilitator
        self.user = User.objects.create_user(
            email="facilitator@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an Event instance, required for the Activity
        self.event = EventFactory(
            title="Sample Event",
        )

        self.activity = Activity(
            title="Test Activity",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        self.activity.save()

        # Create an ActivityFacilitator instance
        self.activity_facilitator = ActivityFacilitator.objects.create(
            activity=self.activity,
            facilitator=self.profile,
        )

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns 'facilitator name for activity title'.
        """
        expected_str = f"{self.profile.get_full_name()} for {self.activity.title}"

        self.assertEqual(str(self.activity_facilitator), expected_str)

    def test_facilitator_relationship(self):
        """
        Test that the facilitator is correctly linked to the ActivityFacilitator.
        """
        self.assertEqual(
            self.activity_facilitator.facilitator,
            self.profile,
        )

    def test_activity_relationship(self):
        """
        Test that the activity is correctly linked to the ActivityFacilitator.
        """
        self.assertEqual(
            self.activity_facilitator.activity,
            self.activity,
        )

    def test_facilitator_activity_relationship_in_reverse(self):
        """
        Test that the facilitators related name in the Activity model returns
        the correct ActivityFacilitator.
        """
        self.assertIn(
            self.activity_facilitator,
            self.activity.facilitators.all(),
        )

    def test_create_facilitator_without_activity(self):
        """
        Test that creating an ActivityFacilitator without an activity raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ActivityFacilitator.objects.create(
                facilitator=self.profile,
                activity=None,
            )


class TestActivityFacilitatorInvitation(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to act as the facilitator
        self.user = User.objects.create_user(
            email="facilitator@example.com",
            password="password123",
        )
        self.profile = self.user.profile  # Using the preferred method to create profile

        # Create an Event instance, required for the Activity
        self.event = EventFactory(
            title="Sample Event",
        )

        # Create an Activity instance
        self.activity = Activity.objects.create(
            title="Test Activity",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        # Create an ActivityFacilitatorInvitation instance
        self.invitation = ActivityFacilitatorInvitation.objects.create(
            activity=self.activity,
            facilitator=self.profile,
            status="Pending",
            invitation_message="You are invited to facilitate this activity.",
        )

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns the correct format.
        """
        expected_str = (
            f"Invitation for {self.profile.get_full_name()} to "
            f"facilitate {self.activity.title}"
        )
        self.assertEqual(str(self.invitation), expected_str)

    def test_invitation_status(self):
        """
        Test that the invitation status can be set and retrieved correctly.
        """
        self.invitation.status = "Accepted"
        self.invitation.save()

        self.assertEqual(self.invitation.status, "Accepted")

    def test_invitation_message(self):
        """
        Test that the invitation message can be set and retrieved correctly.
        """
        message = "Please confirm your participation."
        self.invitation.invitation_message = message
        self.invitation.save()

        self.assertEqual(self.invitation.invitation_message, message)

    def test_unique_invitation(self):
        """
        Test that creating a duplicate invitation raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ActivityFacilitatorInvitation.objects.create(
                activity=self.activity,
                facilitator=self.profile,
                status="Pending",
            )

    def test_invitation_without_facilitator(self):
        """
        Test that creating an invitation without a facilitator raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ActivityFacilitatorInvitation.objects.create(
                activity=self.activity,
                facilitator=None,
            )


class TestActivityFeedback(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a user and associated profile to give feedback
        self.user = User.objects.create_user(
            email="participant@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an Event instance, required for the Activity
        self.event = EventFactory(
            title="Sample Event",
        )

        # Create an Activity instance
        self.activity = Activity.objects.create(
            title="Test Activity",
            event=self.event,
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
        )

        # Create an ActivityFeedback instance
        self.feedback = ActivityFeedback.objects.create(
            activity=self.activity,
            profile=self.profile,
            rating=4,
            comment="Great activity!",
        )

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns 'Feedback for activity
        title by participant name'.
        """
        expected_str = (
            f"Feedback for {self.activity.title} by " f"{self.profile.get_full_name()}"
        )
        self.assertEqual(str(self.feedback), expected_str)

    def test_activity_relationship(self):
        """
        Test that the activity is correctly linked to the ActivityFeedback.
        """

        self.assertEqual(
            self.feedback.activity,
            self.activity,
        )

    def test_profile_relationship(self):
        """
        Test that the profile is correctly linked to the ActivityFeedback.
        """

        self.assertEqual(
            self.feedback.profile,
            self.profile,
        )

    def test_rating_range(self):
        """
        Test that an ActivityFeedback can only be created with a rating between 1 and 5.
        """
        with self.assertRaises(ValidationError):
            feedback = ActivityFeedback(
                activity=self.activity,
                profile=self.profile,
                rating=6,
            )
            feedback.full_clean()

        with self.assertRaises(ValidationError):
            feedback = ActivityFeedback(
                activity=self.activity,
                profile=self.profile,
                rating=0,
            )
            feedback.full_clean()

    def test_create_feedback_without_activity(self):
        """
        Test that creating an ActivityFeedback without an activity raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ActivityFeedback.objects.create(
                profile=self.profile,
                rating=3,
                comment="No activity specified",
                activity=None,
            )

    def test_create_feedback_without_profile(self):
        """
        Test that creating an ActivityFeedback without a profile raises an IntegrityError.
        """

        with self.assertRaises(IntegrityError):
            ActivityFeedback.objects.create(
                activity=self.activity,
                rating=3,
                comment="No profile specified",
                profile=None,
            )

    def test_comment_field(self):
        """
        Test that the comment field can be blank.
        """
        feedback_with_blank_comment = ActivityFeedback.objects.create(
            activity=self.activity,
            profile=self.profile,
            rating=5,
            comment="",
        )

        self.assertEqual(
            feedback_with_blank_comment.comment,
            "",
        )
