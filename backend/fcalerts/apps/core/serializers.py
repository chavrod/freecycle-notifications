from rest_framework import serializers

from .models import UserSelectedKeywords


class UserSelectedKeywordsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = UserSelectedKeywords
        fields = ["name"]
