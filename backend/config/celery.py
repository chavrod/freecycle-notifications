import os
import time
from datetime import timedelta

from celery import Celery, shared_task

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("pingcycle")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        timedelta(minutes=5), check_for_products.s(), name="Check for New Products"
    )


@app.task
def check_for_products():
    print("started task. Sleeeping 10")
    time.sleep(10)
    print("Hello")
