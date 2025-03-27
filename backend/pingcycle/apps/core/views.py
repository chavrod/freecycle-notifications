from datetime import timedelta

from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
import sentry_sdk

from .models import Keyword, Chat, ChatLinkingSession
from .serializers import KeywordsSerializer, KeywordsCreationSerializer, ChatsSerializer
from pingcycle.tools import messaging_providers
from config.settings import ENV


@csrf_protect
def ping(request):
    csrf_token = get_token(request)
    response = JsonResponse({"status": "OK", "csrfToken": csrf_token})
    response.set_cookie("csrftoken", csrf_token)
    return response


class KeywordsViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_keywords = Keyword.objects.filter(user=request.user).annotate(
            messages_count=Count("notified_products__messages")
        )
        serializer = KeywordsSerializer(user_keywords, many=True)
        return Response({"keywords": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = KeywordsCreationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            keyword = Keyword.objects.create(
                name=serializer.validated_data["name"], user=request.user
            )
            serializer = KeywordsSerializer(keyword)
            return Response(
                data={"keyword": serializer.data}, status=status.HTTP_201_CREATED
            )

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            keyword = Keyword.objects.get(pk=pk, user=request.user)
            keyword.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Keyword.DoesNotExist:
            return Response(
                {"error": "Keyword not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ChatsViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_chats = Chat.objects.filter(user=request.user).exclude(
            state=Chat.State.SETUP
        )
        serializer = ChatsSerializer(user_chats, many=True)
        return Response({"chats": serializer.data})

    def create(self, request, *args, **kwargs):
        linking_session = ChatLinkingSession.get_or_create_custom(user=request.user)
        return Response(
            data={"linking_session": linking_session.uuid},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            chat = Chat.objects.get(pk=pk, user=request.user)
            chat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Chat.DoesNotExist:
            return Response(
                {"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["post"], detail=True)
    def toggle_state(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise ValidationError("id is required")

        chat = get_object_or_404(Chat, pk=pk, user=request.user)

        if chat.state == Chat.State.SETUP:
            raise ValidationError("Chat is not linked")

        chat.state = (
            Chat.State.INACTIVE
            if chat.state == Chat.State.ACTIVE
            else Chat.State.ACTIVE
        )

        chat.save(update_fields=["state"])

        serializer = ChatsSerializer(chat)
        return Response({"chat": serializer.data})

    @action(methods=["get"], detail=True)
    def get_chat_by_session_uuid(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise ValidationError("UUID is required")
        uuid = pk

        try:
            chat = Chat.objects.get(
                linking_sessions__uuid=uuid, state=Chat.State.ACTIVE, user=request.user
            )
        except Chat.DoesNotExist:
            raise NotFound("No ACTIVE chat with this session uuid")

        return Response(
            data={"active_chat_id": chat.id},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([])
def messaging_provider_webhook(request, provider_key=None):
    try:
        provider = messaging_providers.get_messaging_provider(provider_key)
        provider.handle_webhook(request)
    except Exception as e:
        print("MESSAGING WEBHOOK ERROR:", e)
        if ENV != "DEV":
            with sentry_sdk.new_scope() as scope:
                scope.set_tag("error_type", "messaging_webhook")
                sentry_sdk.capture_exception(e)

    return Response(status=status.HTTP_200_OK)
