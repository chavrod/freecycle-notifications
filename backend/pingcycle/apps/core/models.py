import re
import uuid
from datetime import timedelta
from typing import Optional

from django.utils import timezone
from django.db import models, IntegrityError
from django.conf import settings
from django.db.models import Q, QuerySet
from django.db.models.functions import Greatest
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.search import TrigramStrictWordSimilarity

from rest_framework.exceptions import ValidationError
import sentry_sdk

from config.settings import (
    MAX_KEYWORDS_PER_USER,
    CHAT_TEMP_UUID_MAX_VALID_SECONDS,
    MAX_CHATS_PER_USER,
    MAX_RETRIES_PER_MESSAGE,
    ENV,
)


class KeywordManager(models.Manager):
    def create(self, name, user):
        custom_errors = []

        # Regex to check for any non-alphabetical characters
        non_alpha_re = re.compile("[^a-zA-Z]")

        words = name.split()
        # Word length
        for word in words:
            if len(word) < 3:
                custom_errors.append("Each word must be at least 3 letters long")
            if non_alpha_re.search(word):
                custom_errors.append(
                    "Keywords may only contain alphabetic characters (no numbers or special characters)."
                )

        # Word count per name
        if len(words) > 3:
            custom_errors.append("3 words max")

        # Word count per user
        keyword_count = Keyword.objects.filter(user=user).count()
        if keyword_count >= MAX_KEYWORDS_PER_USER:
            custom_errors.append(
                f"You cannot have more than {MAX_KEYWORDS_PER_USER} keywords"
            )

        # Duplicates specific to the user
        if Keyword.objects.filter(user=user, name=name).exists():
            custom_errors.append("You have already used this keyword.")

        if custom_errors:
            raise ValidationError({"name": custom_errors})

        return super().create(name=name, user=user)


class Keyword(models.Model):
    objects = KeywordManager()

    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="keywords",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "name"], name="unique_user_name_combo")
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name}"


class NotifiedProductManager(models.Manager):
    def find_keyword_matches(self):
        products_qs = NotifiedProduct.objects.filter(
            state=NotifiedProduct.State.CREATED
        )
        if not products_qs:
            print("No new products...")
            return
        # Set to track product IDs that have matched keywords
        matching_product_ids = set()
        # For each keyword linked to an active chat, check if there are any matches
        for keyword in Keyword.objects.filter(
            user__chats__state=Chat.State.ACTIVE
        ).distinct():

            # Annotate the products with their similarity scores for the current keyword
            matched_products = (
                products_qs.annotate(
                    similarity=Greatest(
                        TrigramStrictWordSimilarity(keyword.name, "product_name"),
                        TrigramStrictWordSimilarity(keyword.name, "description"),
                    )
                )
                .filter(similarity__gt=0.3)
                .order_by("-similarity")
            )

            print(
                f"{matched_products.count()} products found for keyword {keyword}: {matched_products}"
            )

            # Track matches
            for product in matched_products:
                # Add the keyword to the product
                product.keywords.add(keyword)
                # Track this product ID as having a keyword match
                matching_product_ids.add(product.id)

        # Update products that did not match any keywords
        products_qs.exclude(id__in=matching_product_ids).update(
            state=NotifiedProduct.State.IRRELEVANT
        )

        # Update products that have matched keywords
        products_qs.filter(id__in=matching_product_ids).update(
            state=NotifiedProduct.State.KEYWORDS_LINKED
        )

    def delete_irrelevant(self):
        irrelevant_products_one_day_old = NotifiedProduct.objects.filter(
            created__lte=timezone.now() - timedelta(days=1),
            state=NotifiedProduct.State.IRRELEVANT,
        )
        print(f"Deleting {irrelevant_products_one_day_old.count()} IRRELEVANT products")
        irrelevant_products_one_day_old.delete()


class NotifiedProduct(models.Model):
    objects = NotifiedProductManager()

    class State(models.TextChoices):
        CREATED = "CREATED"
        KEYWORDS_LINKED = "KEYWORDS_LINKED"
        MESSAGES_CREATED = "MESSAGES_CREATED"
        IRRELEVANT = "IRRELEVANT"

    state = models.CharField(
        max_length=30, choices=State.choices, default=State.CREATED
    )
    product_name = models.CharField(max_length=200)
    external_id = models.IntegerField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=200)
    sublocation = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)
    keywords = models.ManyToManyField(Keyword, related_name="notified_products")
    img = models.URLField(null=True)

    def get_full_url(self):
        return f"https://www.freecycle.org/posts/{self.external_id}"

    def __str__(self):
        return f"{self.product_name} in {self.sublocation} ({self.location}) - {self.created.strftime('%d-%m-%Y')} - {self.get_full_url()}"

    def get_formatted_message(self, users_keywrods: QuerySet[Keyword]):
        """
        Formats all of the relevant product data and only includes
        keywords passed as an argument (related to specific user)

        # TODO: Implemenation could be improved
        """
        # Retrieve keywords and join them with commas
        keywords_list = list(users_keywrods)
        joined_keywords = ", ".join(keywords_list) if keywords_list else "No keywords"

        # Using Markdown v1
        message = (
            f"*{self.product_name}*\n\n"
            f"{self.description or 'No description available'}\n\n"
            f"📍 *Location:* {self.location}{f', {self.sublocation.title()}' if self.sublocation else ''}\n"
            f"🔑 *Linked Keywords:* {joined_keywords}\n\n"
            f"[{self.get_full_url()}]({self.get_full_url()})\n"
        )

        return message


class Chat(models.Model):
    class State(models.TextChoices):
        SETUP = "SETUP"
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    class Provider(models.TextChoices):
        TELEGRAM = "TELEGRAM"

    name = models.CharField(max_length=200, null=True, blank=False)
    number = models.CharField(max_length=200, null=True, blank=False)  # or username
    reference = models.CharField(max_length=200, null=True, blank=False)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="chats",
        on_delete=models.CASCADE,
    )
    state = models.CharField(max_length=30, choices=State.choices, default=State.SETUP)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_valid_linking_session(self) -> Optional["ChatLinkingSession"]:
        assert self.state == Chat.State.SETUP, "Expected chat to be in 'SETUP' state."

        return (
            self.linking_sessions.filter(uuid_expiry__gte=timezone.now())
            .order_by("-uuid_expiry")
            .first()
        )

    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    (Q(state="ACTIVE") & Q(reference__isnull=False))
                    | (Q(state="INACTIVE") & Q(reference__isnull=False))
                    | Q(state="SETUP")
                ),
                name="check_non_null_reference_when_active_or_inactive",
            ),
            UniqueConstraint(
                fields=["reference", "provider"], name="unique_reference_provider_combo"
            ),
        ]


class ChatLinkingSession(models.Model):
    chat = models.ForeignKey(
        Chat, related_name="linking_sessions", on_delete=models.CASCADE
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    uuid_expiry = models.DateTimeField()

    @classmethod
    def get_or_create_custom(cls, user):
        """
        Gets or creates a valid uuid, that Telegram bot can use to uniquely
        identify a user linking a chat.
        """
        # Check users linked chat count
        chats = Chat.objects.filter(
            user=user, state__in=[Chat.State.ACTIVE, Chat.State.INACTIVE]
        )
        if chats.count() > MAX_CHATS_PER_USER:
            raise ValidationError(
                {
                    "detail": f"Total number of linked chats: {MAX_CHATS_PER_USER}. Max allowed number of Chats: {MAX_CHATS_PER_USER}"
                }
            )

        chat = Chat.objects.create(
            number=None,
            reference=None,
            provider=Chat.Provider.TELEGRAM,
            user=user,
            state=Chat.State.SETUP,
        )

        valid_linking_session = chat.get_valid_linking_session()
        if valid_linking_session:
            return valid_linking_session

        new_session = None
        attempts = 0
        while new_session is None:
            try:
                if attempts > 4:  # Extremely unlikely to happen
                    if ENV != "DEV":
                        with sentry_sdk.new_scope() as scope:
                            scope.set_tag("attempts", attempts)
                            scope.user = {"id": user.id, "email": user.email}
                            sentry_sdk.capture_message(
                                "Failed Getting Session UUID", "warning"
                            )
                    raise ValidationError(
                        {"detail": "Something went wrong. Please try again."}
                    )
                uuid_expiry = timezone.now() + timedelta(
                    seconds=CHAT_TEMP_UUID_MAX_VALID_SECONDS
                )
                new_session = ChatLinkingSession.objects.create(
                    chat=chat, uuid_expiry=uuid_expiry
                )
            except IntegrityError:
                print("Failed to create session, reattempting.")
                attempts += 1
                continue

        return new_session


class Message(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED"
        SENT = "SENT"
        FAILED = "FAILED"

    class Sender(models.TextChoices):
        BOT = "BOT"
        USER = "USER"

    notified_product = models.ForeignKey(
        NotifiedProduct, related_name="messages", on_delete=models.SET_NULL, null=True
    )
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=30, choices=Sender.choices)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.CREATED
    )
    retry_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_RETRIES_PER_MESSAGE)],
    )
    error_res_code = models.IntegerField(null=True)
    error_msg = models.CharField(null=True)

    def __str__(self):
        return f"Message to {self.chat} with status {self.status}"
