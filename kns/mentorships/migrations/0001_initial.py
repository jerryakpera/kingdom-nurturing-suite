# Generated by Django 5.1 on 2024-09-12 13:19

import uuid

import django.db.models.deletion
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0003_alter_discipleship_author_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MentorshipArea",
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
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="published",
                        max_length=10,
                    ),
                ),
                ("title", models.CharField(max_length=150, unique=True)),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        null=True,
                        unique=True,
                    ),
                ),
                ("content", tinymce.models.HTMLField()),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mentorship_areas_created",
                        to="profiles.profile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]