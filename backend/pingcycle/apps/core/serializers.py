import re

from rest_framework import serializers

from .models import Keyword, Chat


class KeywordsSerializer(serializers.ModelSerializer):
    messages_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Keyword
        exclude = ["user"]


class KeywordsCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)

    def validate_name(self, value):
        # Remove leading and trailing whitespaces, replace multiple spaces with one, and convert to lowercase
        value = re.sub(r"\s+", " ", value.strip()).title()
        return value

    class Meta:
        model = Keyword
        fields = ["name"]


class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        exclude = ["user"]
