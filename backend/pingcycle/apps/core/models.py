from django.db import models
from django.conf import settings
from django.db.models import Q
from django.db.models.constraints import CheckConstraint

from rest_framework.exceptions import ValidationError

from config.settings import MAX_KEYWORDS_PER_USER


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
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_user_name_combo"
            )
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name}"


class NotifiedProduct(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED"
        SENT = "SENT"
        SENDING_FAILED = "SENDING_FAILED"

    product_name = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=Status.choices)
    external_id = models.IntegerField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=200)
    sublocation = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)
    keywords = models.ManyToManyField(Keyword, related_name="notified_products")
    img = models.URLField(null=True)
    # TODO: img url for a nice preview??

    def get_full_url(self):
        return f"https://www.freecycle.org/posts/{self.external_id}"

    def __str__(self):
        return f"{self.name} in {self.sublocation} ({self.location}) - {self.created.strftime('%d-%m-%Y')} - {self.get_full_url()}"


class Chat(models.Model):
    class State(models.TextChoices):
        SETUP = "SETUP"
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    class Provider(models.TextChoices):
        TELEGRAM = "TELEGRAM"

    temp_uuid = models.UUIDField(unique=True, null=True)
    number = models.CharField(max_length=200, null=True, blank=False)  # or username
    reference = models.CharField(
        max_length=200, null=True, blank=False
    )  # TODO: must be unique per provider
    provider = models.CharField(max_length=10, choices=Provider.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="messages", on_delete=models.PROTECT
    )
    state = models.CharField(max_length=30, choices=State.choices, default=State.SETUP)

    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    (
                        Q(state="ACTIVE")
                        & Q(number__isnull=False)
                        & Q(reference__isnull=False)
                    )
                    | (
                        Q(state="INACTIVE")
                        & Q(number__isnull=False)
                        & Q(reference__isnull=False)
                    )
                ),
                name="check_non_null_number_reference_when_active_or_inactive",
            ),
        ]

    # TODO: add a constraint that only allows null values for SETUP state
    # TODO: limit one user per chat + serilizer
