from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0011_remove_chat_check_non_null_number_reference_when_active_or_inactive_and_more",
        ),
    ]

    operations = [
        TrigramExtension(),
    ]
