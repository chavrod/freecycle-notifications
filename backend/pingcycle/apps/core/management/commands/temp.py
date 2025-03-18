from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from config.settings import SITE_ID, APP_NAME, BASE_DOMAIN
import pingcycle.apps.core.models as core_models


class Command(BaseCommand):
    help = "Update the site domain and name."

    # user:  test@pingcycle.org
    # user:  dchavro@gmail.com

    def handle(self, *args, **kwargs):
        User = get_user_model()

        dima = User.objects.get(email="dchavro@gmail.com")
        some_guy = User.objects.get(email="test@pingcycle.org")

        core_models.Chat.objects.all().delete()
        core_models.NotifiedProduct.objects.all().delete()
        core_models.Keyword.objects.all().delete()

        chat_dima_1 = core_models.Chat.objects.create(
            name="chat_dima_1",
            number="chat_dima_1",
            reference="chat_dima_1",
            provider=core_models.Chat.Provider.TELEGRAM,
            user=dima,
            state=core_models.Chat.State.ACTIVE,
        )
        chat_dima_2 = core_models.Chat.objects.create(
            name="chat_dima_2",
            number="chat_dima_2",
            reference="chat_dima_2",
            provider=core_models.Chat.Provider.TELEGRAM,
            user=dima,
            state=core_models.Chat.State.INACTIVE,
        )
        chat_some_guy_1 = core_models.Chat.objects.create(
            name="chat_some_guy_1",
            number="chat_some_guy_1",
            reference="chat_some_guy_1",
            provider=core_models.Chat.Provider.TELEGRAM,
            user=some_guy,
            state=core_models.Chat.State.ACTIVE,
        )

        keyword_dima_1 = core_models.Keyword.objects.create(
            name="keyword_dima_1", user=dima
        )
        keyword_dima_2 = core_models.Keyword.objects.create(
            name="keyword_dima_2", user=dima
        )
        keyword_dima_3 = core_models.Keyword.objects.create(
            name="keyword_dima_3", user=dima
        )

        keyword_some_guy_1 = core_models.Keyword.objects.create(
            name="keyword_some_guy_1", user=some_guy
        )
        keyword_some_guy_2 = core_models.Keyword.objects.create(
            name="keyword_some_guy_2", user=some_guy
        )
        keyword_some_guy_3 = core_models.Keyword.objects.create(
            name="keyword_some_guy_3", user=some_guy
        )

        notified_product_1 = core_models.NotifiedProduct.objects.create(
            product_name="notified_product_1",
            external_id=1,
            location="Dub",
        )
        notified_product_1.keywords.set(
            [keyword_dima_1, keyword_dima_2, keyword_some_guy_1]
        )
        notified_product_1.save()

        notified_product_2 = core_models.NotifiedProduct.objects.create(
            product_name="notified_product_2",
            external_id=2,
            location="Dub",
        )
        notified_product_2.keywords.set(
            [keyword_dima_2, keyword_dima_3, keyword_some_guy_2]
        )
        notified_product_2.save()

        def get_products_to_send():
            products = core_models.NotifiedProduct.objects.filter().prefetch_related(
                "keywords__user__chats"
            )
            products_chats_keywords = []
            for product in products:
                chats_keywords = {}

                matched_keywords = product.keywords.all()
                for matched_keyword in matched_keywords:
                    chats = matched_keyword.user.chats.all()

                    for chat in chats:
                        if chat.state != core_models.Chat.State.ACTIVE:
                            continue
                        # Initialize the list if the user key doesn't exist
                        if chat not in chats_keywords:
                            chats_keywords[chat] = []
                        chats_keywords[chat].append(matched_keyword)

                if chats_keywords:
                    products_chats_keywords.append([product, chats_keywords])

            return products_chats_keywords

        products = get_products_to_send()

        for product, chat_keywords in products:
            print("product_name: ", product.product_name)
            for chat, keywords in chat_keywords.items():
                print(
                    f"to chat with name: {chat.name} will send with matched keywords {keywords}"
                )
