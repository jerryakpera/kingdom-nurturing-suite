# Generated by Django 5.1 on 2024-10-16 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding", "0006_profilecompletiontask_task_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="profilecompletion",
            name="is_dismissed",
            field=models.BooleanField(default=False),
        ),
    ]