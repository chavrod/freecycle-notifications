from django.contrib.auth import get_user_model

import pytest

import pingcycle.apps.core.models as core_models

User = get_user_model()


@pytest.mark.django_db
@pytest.fixture
def get_or_create_user_chats_keywords_products():
    def _get_or_create_user_chats_keywords_products(
        username: str = "user1",
        chats: list = [
            {
                "reference": "chat_1_user1",
            },
        ],
        keywords_products: dict = {
            "apple": [
                {
                    "product_name": "hot apple pie",
                    "external_id": 1,
                },
            ]
        },
    ):
        user, _ = User.objects.get_or_create(
            username=username,
            email=f"{username}@pingcycle.org",
        )

        for chat in chats:
            chat, _ = core_models.Chat.objects.get_or_create(
                reference=chat["reference"],
                provider=core_models.Chat.Provider.TELEGRAM,
                user=user,
                state=chat.get("state", core_models.Chat.State.ACTIVE),
            )

        for keyword, products in keywords_products.items():
            keyword, _ = core_models.Keyword.objects.get_or_create(
                name=keyword, user=user
            )
            for product in products:
                product, _ = core_models.NotifiedProduct.objects.get_or_create(
                    product_name=product["product_name"],
                    messages_scheduled=product.get("messages_scheduled", False),
                    external_id=product["external_id"],
                    location="Test Location",
                )
                product.keywords.add(keyword)

    return _get_or_create_user_chats_keywords_products


@pytest.mark.django_db
@pytest.fixture
def user_2():
    return User.objects.create(
        username="user_1",
        email="user1@pingcycle.org",
    )
