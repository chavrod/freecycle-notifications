# Generated by Django 5.1.6 on 2025-03-07 08:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_rename_content_message_text_remove_message_sent_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chatlinkingsession",
            name="uuid_created",
        ),
        migrations.AddField(
            model_name="chatlinkingsession",
            name="uuid_expiry",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 3, 7, 8, 14, 20, 521249, tzinfo=datetime.timezone.utc
                )
            ),
            preserve_default=False,
        ),
    ]
