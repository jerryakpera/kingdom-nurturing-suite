# Generated by Django 5.1 on 2024-10-04 11:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0007_profile_email_token_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="reason_is_not_mentor",
            field=models.TextField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(100),
                    django.core.validators.MaxLengthValidator(500),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="reason_is_not_movement_training_facilitator",
            field=models.TextField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(100),
                    django.core.validators.MaxLengthValidator(500),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="reason_is_not_skill_training_facilitator",
            field=models.TextField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(100),
                    django.core.validators.MaxLengthValidator(500),
                ],
            ),
        ),
    ]
