# Generated by Django 5.1 on 2024-10-17 13:15

import uuid

import cloudinary.models
import django.core.validators
import django.db.models.deletion
import taggit.managers
import tinymce.models
from django.db import migrations, models

import kns.events.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("events", "0003_remove_event_registration_limit_alter_event_slug_and_more"),
        ("profiles", "0009_alter_consentform_reject_reason_and_more"),
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=150)),
                ("description", tinymce.models.HTMLField()),
                (
                    "summary",
                    models.TextField(
                        validators=[
                            django.core.validators.MinLengthValidator(
                                135,
                                message="Summary must be at least 135 characters long",
                            ),
                            django.core.validators.MaxLengthValidator(
                                200,
                                message="Summary must be no more than 200 characters long",
                            ),
                        ]
                    ),
                ),
                ("slug", models.SlugField(editable=False, unique=True)),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("skill_training", "Skill Training"),
                            ("movement_training", "Movement Training"),
                            ("community_service", "Community Service"),
                            ("prayer_movement", "Prayer Movement"),
                        ],
                        max_length=50,
                    ),
                ),
                ("meeting_link", models.URLField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField(blank=True, null=True)),
                ("capacity", models.PositiveIntegerField(default=0)),
                (
                    "default_facilitation_invitation_message",
                    models.TextField(blank=True, null=True),
                ),
                ("requirements", tinymce.models.HTMLField(blank=True, null=True)),
                (
                    "scope",
                    models.CharField(
                        choices=[
                            ("comprehensive", "Comprehensive"),
                            ("abridged", "Abridged"),
                        ],
                        default="comprehensive",
                        max_length=20,
                    ),
                ),
                (
                    "beneficiary",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities_organized",
                        to="profiles.profile",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="events.event",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Activities",
                "ordering": ["start_date"],
            },
        ),
        migrations.CreateModel(
            name="ActivityFacilitator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facilitators",
                        to="activities.activity",
                    ),
                ),
                (
                    "facilitator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facilitated_activities",
                        to="profiles.profile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActivityFeedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks",
                        to="activities.activity",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_feedbacks",
                        to="profiles.profile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActivityImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True,
                        max_length=255,
                        null=True,
                        validators=[kns.events.utils.validate_image],
                    ),
                ),
                ("caption", models.TextField(blank=True, null=True)),
                ("primary", models.BooleanField(default=False)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="activities.activity",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActivityRegistration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Cancelled", "Cancelled"),
                            ("Confirmed", "Confirmed"),
                            ("Registered", "Registered"),
                        ],
                        default="Registered",
                        max_length=20,
                    ),
                ),
                ("guest_name", models.CharField(blank=True, max_length=150, null=True)),
                (
                    "guest_email",
                    models.EmailField(blank=True, max_length=150, null=True),
                ),
                ("is_guest", models.BooleanField(default=False)),
                (
                    "confirmation_token",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "rejection_token",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registrations",
                        to="activities.activity",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_registrations",
                        to="profiles.profile",
                    ),
                ),
            ],
            options={
                "ordering": ["activity", "guest_name"],
            },
        ),
        migrations.CreateModel(
            name="ActivityAttendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("check_in_time", models.DateTimeField(blank=True, null=True)),
                (
                    "registration",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance",
                        to="activities.activityregistration",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActivityFacilitatorInvitation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Accepted", "Accepted"),
                            ("Rejected", "Rejected"),
                        ],
                        default="Pending",
                        max_length=20,
                    ),
                ),
                ("invitation_message", models.TextField(blank=True, null=True)),
                (
                    "confirmation_token",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "rejection_token",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facilitator_invitations",
                        to="activities.activity",
                    ),
                ),
                (
                    "facilitator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facilitator_invitations",
                        to="profiles.profile",
                    ),
                ),
            ],
            options={
                "unique_together": {("activity", "facilitator")},
            },
        ),
    ]
