from django.db import models
from django.conf import settings

from rest_framework.exceptions import ValidationError

from config.settings import MAX_KEYWORDS_PER_USER


class UserSelectedKeywordsManager(models.Manager):
    def create(self, name, user):
        keyword_count = UserSelectedKeywords.objects.filter(user=user).count()

        if keyword_count >= MAX_KEYWORDS_PER_USER:
            raise ValidationError(
                {
                    "name": [
                        f"You cannot have more than {MAX_KEYWORDS_PER_USER} keywords"
                    ]
                }
            )
        return super().create(name=name, user=user)


class UserSelectedKeywords(models.Model):
    objects = UserSelectedKeywordsManager()

    name = models.CharField(max_length=200)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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

    status = models.CharField(max_length=30, choices=Status.choices)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    external_id = models.IntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    sublocation = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    # TODO: img url for a nice preview??

    def get_full_url(self):
        return f"https://www.freecycle.org/posts/{self.external_id}"

    def __str__(self):
        return f"{self.name} in {self.sublocation} ({self.location}) - {self.created.strftime('%d-%m-%Y')} - {self.get_full_url()}"
