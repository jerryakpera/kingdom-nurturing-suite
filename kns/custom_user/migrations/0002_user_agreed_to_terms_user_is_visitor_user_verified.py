# Generated by Django 5.1 on 2024-08-16 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="agreed_to_terms",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_visitor",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="verified",
            field=models.BooleanField(default=False),
        ),
    ]