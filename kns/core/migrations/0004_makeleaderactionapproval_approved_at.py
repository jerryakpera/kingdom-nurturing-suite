# Generated by Django 5.1 on 2024-09-03 14:22

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_makeleaderactionapproval_read_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="makeleaderactionapproval",
            name="approved_at",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2024, 9, 3, 14, 22, 47, 38854, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
    ]