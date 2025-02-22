from django.db import models
from django.conf import settings

from rest_framework.exceptions import ValidationError

from config.settings import MAX_KEYWORDS_PER_USER


class KeywordManager(models.Manager):
    def create(self, name, user):
        keyword_count = Keyword.objects.filter(user=user).count()

        if keyword_count >= MAX_KEYWORDS_PER_USER:
            raise ValidationError(
                {
                    "name": [
                        f"You cannot have more than {MAX_KEYWORDS_PER_USER} keywords"
                    ]
                }
            )
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
