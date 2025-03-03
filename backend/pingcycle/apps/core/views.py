from datetime import timedelta

from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Keyword, Chat, ChatLinkingSession
from .serializers import KeywordsSerializer, KeywordsCreationSerializer


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
        user_keywords = Keyword.objects.filter(user=request.user)
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

    # TODO: Move heavy logic into model???
    @action(methods=["post"], detail=False)
    def link_chat(self, request, *args, **kwargs):
        print("Request to LINK CHAT. Checking for existing chats...")
        user = request.user
        # Check if user already has a linked chat
        chat = Chat.objects.filter(user=user).first()
        if chat and chat.state in [Chat.State.ACTIVE, Chat.State.INACTIVE]:
            print("Found linked chat. Aborting")
            return Response(
                {
                    "detail": "You already have linked chat. You can unlink your existing chat."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        assert chat.state == Chat.State.SETUP, "Expected chat to be in 'SETUP' state."
        print("No linked chats. Continue")
        # TODO: move to settings
        CHAT_TEMP_UUID_MAX_VALID_SECONDS = 20
        cutoff_time = timezone.now() - timedelta(
            seconds=CHAT_TEMP_UUID_MAX_VALID_SECONDS
        )
        valid_linking_session: ChatLinkingSession = (
            chat.linking_sessions.filter(
                temp_uuid__is_null=False, temp_uuid_created__gte=cutoff_time
            )
            .order_by("-temp_uuid_created")
            .first()
        )
        if valid_linking_session:
            print(
                "Found Valid linking_session: ",
                valid_linking_session.temp_uuid,
                valid_linking_session.temp_uuid_created,
            )
            return Response(
                data={"linking_session": valid_linking_session},
                status=status.HTTP_200_OK,
            )

        # Ensure we do not get duplicate uuid.
        # TODO: Test + max attempts?? Is there better way? Or better uuid?
        print("Attempting to create linking_session")
        new_session = None
        while new_session is None:
            try:
                new_session = ChatLinkingSession.objects.create(chat=chat)
                print(
                    "Created linking_session: ",
                    new_session.temp_uuid,
                )
            except IntegrityError:
                print("Failed to create session, reattempting.")
                # TODO: Log!
                continue

        return Response(
            data={"linking_session": new_session},
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False)
    def unlink_chat(self, request, *args, **kwargs):
        pass
