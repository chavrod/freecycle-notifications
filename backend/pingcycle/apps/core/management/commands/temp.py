import asyncio

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.db.models.functions import Greatest
from django.contrib.postgres.search import (
    TrigramSimilarity,
    TrigramDistance,
    TrigramBase,
    TrigramStrictWordSimilarity,
)
from django.db.models.functions import Greatest
from django.db.models import Q

from pingcycle.tools.scraper import Scraper
from pingcycle.tools.messaging_scheduler import MessageScheduler
from pingcycle.tools.messaging_providers import get_messaging_provider
import pingcycle.apps.core.models as core_models

# Ninja Foodi
# Ninja Foofdi, 3-in-1 blender, with accessories.
# Like new, rarely used. original post date: 2025-03-21
# core_models.NotifiedProduct.objects.create(
#     product_name="Ninja Foodi",
#     external_id=111,
#     description="Ninja Foofdi, 3-in-1 blender, with accessories. Like new, rarely used. original post date: 2025-03-21",
#     location="TEST",
#     sublocation="TEST",
# )


# Offer: 2 seater leather couch
# Free to go - 2 seater leather sofa. Good condition
# apart from some claw marks from a cat (shown in photos) Must...

# User = get_user_model()
# dima = User.objects.get(email="dchavro@gmail.com")
# print(dima)

# core_models.Keyword.objects.create(name="blender", user=dima)
# core_models.Keyword.objects.create(name="sofa", user=dima)


class Command(BaseCommand):
    help = "Update the site domain and name."

    # user:  test@pingcycle.org
    # user:  dchavro@gmail.com

    def handle(self, *args, **kwargs):
        pass
        # prods = core_models.NotifiedProduct.objects.all()
        # prods.delete()

        # print("Start scraping")
        scraper = Scraper()
        asyncio.run(scraper.run_main(with_proxy=False))

        # print("Products scraped")
        # for product in core_models.NotifiedProduct.objects.all():
        #     print(product.product_name, product.state, product.keywords.all().count())

        # core_models.NotifiedProduct.objects.find_keyword_matches()
        # print("Kewords linked")
        # for product in core_models.NotifiedProduct.objects.all():
        #     print(product.product_name, product.state, product.keywords.all().count())

        # telegram_provider = get_messaging_provider(core_models.Chat.Provider.TELEGRAM)
        # scheduler = MessageScheduler(provider=telegram_provider)
        # scheduler.send_notified_products_in_queue()
        # print("Messages sent")
        # for product in core_models.NotifiedProduct.objects.all():
        #     print(product.product_name, product.state, product.keywords.all().count())

        # core_models.NotifiedProduct.objects.delete_irrelevant()
        # print("Irrelevant deleted")
        # for product in core_models.NotifiedProduct.objects.all():
        #     print(product.product_name, product.state, product.keywords.all().count())

        # notified_products = (
        #     core_models.NotifiedProduct.objects.alias(
        #         similarity_score=TrigramSimilarity("product_name", keyword)
        #     )
        #     .filter(
        #         similarity_score__gt=0.3
        #     )  # Adjust the similarity threshold as needed
        #     .order_by("-similarity_score")  # Optionally order by similarity score
        # )
        # notified_products = core_models.NotifiedProduct.objects.filter(
        #     product_name__trigram_strict_word_similar=keyword
        # )
        # print(f"notified_products for keyword '{keyword}': ", notified_products)

        # pass


# print("Start scraping")
# scraper = Scraper()
# asyncio.run(scraper.run_main())

# telegram_provider = get_messaging_provider(core_models.Chat.Provider.TELEGRAM)
# scheduler = MessageScheduler(provider=telegram_provider)
# scheduler.send_notified_products_in_queue()
