import uuid
from datetime import timedelta
from typing import Optional

from django.utils import timezone
from django.db import models, IntegrityError
from django.conf import settings
from django.db.models import Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework.exceptions import ValidationError

from config.settings import (
    MAX_KEYWORDS_PER_USER,
    CHAT_TEMP_UUID_MAX_VALID_SECONDS,
    MAX_CHATS_PER_USER,
    MAX_RETRIES_PER_MESSAGE,
)


class KeywordManager(models.Manager):
    def create(self, name, user):
        custom_errors = []

        words = name.split()
        # Word length
        for word in words:
            if len(word) < 3:
                custom_errors.append("Each word must be at least 3 letters long")
                break
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


class NotifiedProduct(models.Model):
    messages_scheduled = models.BooleanField(default=False)
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


class Chat(models.Model):
    class State(models.TextChoices):
        SETUP = "SETUP"
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    class Provider(models.TextChoices):
        TELEGRAM = "TELEGRAM"

    name = models.CharField(max_length=200, null=True, blank=False)
    number = models.CharField(max_length=200, null=True, blank=False)  # or username
    reference = models.CharField(
        max_length=200, null=True, blank=False
    )  # TODO: must be unique per provider
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
                    # TODO: SENTRY!
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
