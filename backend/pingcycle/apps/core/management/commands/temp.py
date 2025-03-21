import asyncio

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from pingcycle.tools.scraper import Scraper
from pingcycle.tools.messaging_scheduler import MessageScheduler
from pingcycle.tools.messaging_providers import get_messaging_provider
import pingcycle.apps.core.models as core_models


class Command(BaseCommand):
    help = "Update the site domain and name."

    # user:  test@pingcycle.org
    # user:  dchavro@gmail.com

    def handle(self, *args, **kwargs):
        # print("Start scraping")
        # scraper = Scraper()
        # asyncio.run(scraper.run_main())

        # messages = core_models.Message.objects.all()
        # messages.delete()

        # telegram_provider = get_messaging_provider(core_models.Chat.Provider.TELEGRAM)
        # scheduler = MessageScheduler(provider=telegram_provider)
        # scheduler.send_notified_products_in_queue()
        pass
