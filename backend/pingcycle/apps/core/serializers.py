from rest_framework import serializers

from .models import Keyword


class KeywordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        exclude = ["user"]


class KeywordsCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Keyword
        fields = ["name"]
