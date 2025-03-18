# Generated by Django 5.1.6 on 2025-03-18 09:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_remove_notifiedproduct_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="retry_count",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
            ),
        ),
    ]
