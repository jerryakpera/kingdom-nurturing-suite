# Generated by Django 5.1 on 2024-09-26 06:48

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("groups", "0001_initial"),
        ("profiles", "0004_profile_is_onboarded"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActionApproval",
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
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("expired", "Expired"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("read", models.BooleanField(default=False)),
                (
                    "timeout_duration",
                    models.DurationField(default=datetime.timedelta(days=7)),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_actions",
                        to="profiles.profile",
                    ),
                ),
                (
                    "consumer_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_requests",
                        to="groups.group",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="initiated_approvals",
                        to="profiles.profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PromoteToLeaderRole",
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
                    "approval",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="promote_to_leader_action",
                        to="actionapprovals.actionapproval",
                    ),
                ),
                (
                    "new_leader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leader_promotions",
                        to="profiles.profile",
                    ),
                ),
            ],
        ),
    ]
