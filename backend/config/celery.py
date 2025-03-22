import os
from datetime import timedelta
from asgiref.sync import async_to_sync

from celery import Celery

from config.settings import TASKS_INTERVAL_MINUTES

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
        timedelta(minutes=TASKS_INTERVAL_MINUTES),
        look_for_new_products_task_and_notify.s(),
        name="Check for new products & notify",
    )

    sender.add_periodic_task(
        timedelta(minutes=TASKS_INTERVAL_MINUTES),
        delete_old_irrelevant_products.s(),
        name="Delete old irrelevant products",
    )


async def look_for_new_products():
    from pingcycle.tools.scraper import Scraper

    scraper = Scraper()
    await scraper.run_main()


@app.task
def look_for_new_products_task_and_notify():
    from pingcycle.tools.messaging_scheduler import MessageScheduler
    from pingcycle.tools.messaging_providers import get_messaging_provider
    import pingcycle.apps.core.models as core_models

    async_to_sync(look_for_new_products)()

    core_models.NotifiedProduct.objects.find_keyword_matches()

    telegram_provider = get_messaging_provider(core_models.Chat.Provider.TELEGRAM)
    scheduler = MessageScheduler(provider=telegram_provider)
    scheduler.send_notified_products_in_queue()


@app.task
def delete_old_irrelevant_products():
    import pingcycle.apps.core.models as core_models

    core_models.NotifiedProduct.objects.delete_irrelevant()
