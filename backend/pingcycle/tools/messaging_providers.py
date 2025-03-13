from datetime import timedelta
from typing import Optional, Tuple, List, Dict
import requests
import uuid

from django.utils import timezone
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

import pingcycle.apps.core.models as core_models
from config.settings import (
    BASE_ORIGIN,
    WH_BASE_DOMAIN,
    CONFIG,
)


class UserFriendlyChatError(Exception):
    """
    Raised when we want to respond to the user
    with a useful message e.g. setup uuid token expired
    """

    def __init__(self, message, **kwargs):
        self.message = message
        self.chat_reference = kwargs.get("chat_reference")
        super().__init__(self.message)


class MessagingProvider:
    key: str = None

    CHAT_LIMIT_SECONDS: Tuple[int, int] = None
    TOTAL_LIMIT_SECONDS: Tuple[int, int] = None

    def __init__(self):
        self._rate_limit_count = 10
        self._rate_limit_time = timedelta(seconds=10)
        self._has_image_capability = False
        if self.key is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a value for `key`"
            )

    @staticmethod
    def bold(text: str) -> str:
        return text

    @staticmethod
    def italic_or_quote(text: str) -> str:
        return text

    def _get_webhook_url(self):
        raise NotImplementedError(
            f"{self.__class__.__name__}._get_webhook_url() not implemented."
        )

    def _get_or_create_chat(self, data) -> Tuple[core_models.Chat | None, bool]:
        raise NotImplementedError(
            f"{self.__class__.__name__}._get_or_create_chat() not implemented."
        )

    def _get_ref(self, data) -> Optional[str]:
        raise NotImplementedError(
            f"{self.__class__.__name__}._get_ref() not implemented."
        )

    def _get_text(self, data) -> str | None:
        raise NotImplementedError(
            f"{self.__class__.__name__}._get_text() not implemented."
        )

    def send_message(self, message):
        raise NotImplementedError(
            f"{self.__class__.__name__}.send_message() not implemented."
        )

    def handle_webhook(self, request: requests.Request):
        raise NotImplementedError(
            f"{self.__class__.__name__}.handle_webhook_data() not implemented."
        )

    def health_check(self):
        raise NotImplementedError(
            f"{self.__class__.__name__}.health_check() not implemented."
        )

    # TODO: Format product message
    def _set_formatted_product_message_text(self, message: core_models.Message):
        return message.text
        message.text = result
        message.save()

    def _receive_message(self, data):
        chat, created = self._get_or_create_chat(data)
        # text = self._get_text(data)

        if created:
            self._send_welcome_message(chat)
            return
        # Any messages from unlinked chats are ignored
        if chat is None:
            return

        # Check rate limit for the specific chat

        # Decide how to respond

    def _send_welcome_message(self, chat: core_models.Chat):
        user_email = chat.user.email
        link = f"{BASE_ORIGIN}/dashboard"
        text = (
            f"👋 Hello from PingCycle, {chat.name}!\n\n"
            f"We have linked 🔗 this number to your existing account {self.bold(user_email)}\n\n"
            f"🔙 Head back to {link} to add keywords 🔑 and start collecting them freebies 😎"
        )
        message = core_models.Message.objects.create(
            chat=chat,
            text=text,
            sender=core_models.Message.Sender.USER,
        )
        self.send_message(message)

    # def _on_rate_limit_exceeded(self, message):
    #     print("MESSAGE EXCEEDS RATE LIMIT:", message)
    #     # SENTRY
    #     capture_message(
    #         f"Rate limit exceeded for chat ID {message.chat.id} with message: {message}"
    #     )

    def _get_valid_linking_session(
        self, potential_uuid, chat_reference
    ) -> core_models.ChatLinkingSession:
        # Validate if it's a proper UUID v4
        try:
            extracted_uuid = uuid.UUID(potential_uuid, version=4)
        except (ValueError, AttributeError):
            raise ValueError("Invalid UUID v4")

        # Check if the UUID has the correct format (ensures it's not a valid UUID of a different version)
        if str(extracted_uuid) != potential_uuid:
            raise ValueError("Provided UUID is not a valid v4 UUID")

        try:
            linking_session = core_models.ChatLinkingSession.objects.get(
                uuid=extracted_uuid
            )
        except core_models.ChatLinkingSession.DoesNotExist:
            print("No sessions match provided uuid")
            raise ValidationError("No sessions match provided uuid")

        expiry_datetime = linking_session.uuid_expiry
        if expiry_datetime < timezone.now():
            print("Expired linking session, raising error")
            raise UserFriendlyChatError(
                message="Your linking session has expired 😢\n\n"
                f"🔙 Head back to the app and try again: {BASE_ORIGIN}/dashboard\n\n"
                "If the issue persists, contact help@pingcycle.org",
                chat_reference=chat_reference,
            )

        return linking_session


class Telegram(MessagingProvider):
    key = core_models.Chat.Provider.TELEGRAM

    CHAT_LIMIT_SECONDS = (1, 1)
    TOTAL_LIMIT_SECONDS = (30, 1)

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.telegram.org"
        self.bot_username = CONFIG["TELEGRAM_BOT_USERNAME"]
        self.bot_token = CONFIG["TELEGRAM_BOT_TOKEN"]
        self.webhook_secret = CONFIG["TELEGRAM_WEBHOOK_SECRET"]
        self._setup_webhook()

    @staticmethod
    def bold(text: str) -> str:
        return f"*{text}*"

    @staticmethod
    def italic_or_quote(text: str) -> str:
        return f"_{text}_"

    def _post_api(self, method_name: str, **params):
        """
        Makes POST request to Telegram API with the provided method name and additional parameters,
        and returns JSON.

        :param method_name: The API method name to call.
        :param params: Additional parameters for the API request.
        :return: JSON response from the API.
        :raises: Exception if the response status code is not 200.
        """
        url = f"{self.api_url}/bot{self.bot_token}/{method_name}"
        res = requests.post(url, json=params)

        status_code = res.status_code
        assert (
            status_code == 200
        ), f"Expected 200 for {method_name} (params: {params}) but got {status_code} {res.text}"

        return res.json()

    def handle_webhook(self, request: requests.Request):
        print("RECEIVED MESSAGE")
        data = request.data
        message = data.get("message")

        if message:
            try:
                secret_token = request.headers["X-Telegram-Bot-Api-Secret-Token"]
                if secret_token != self.webhook_secret:
                    return Response(status=status.HTTP_200_OK)

                self._receive_message(data)
            except UserFriendlyChatError as e:
                self._post_api(
                    "sendMessage",
                    chat_id=e.chat_reference,
                    text=e.message,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print("ERROR TELEGRAM handle_webhook(): ", e)
                # TODO: SENTRY
                # capture_exception(e)
        else:
            print("UNHANDLED EVENT TELEGRAM TYPE:", request.data)

        return Response(status=status.HTTP_200_OK)

    def _get_or_create_chat(self, data):
        message_from = data["message"]["from"]
        from_id = message_from["id"]

        message_text = data["message"]["text"]
        attempting_to_link_chat = message_text.startswith("/start ")

        try:
            existing_chat = core_models.Chat.objects.get(
                reference=from_id,
                provider=core_models.Chat.Provider.TELEGRAM,
            )
            if attempting_to_link_chat:
                raise UserFriendlyChatError(
                    message=(
                        f"⛔️ This chat is already associated with an account: {existing_chat.user.email}\n\n"
                        f"If you want to link this chat to the new account, first unlink it from the old account.\n\n"
                        f"🔙 Log in to the app with the old account: {BASE_ORIGIN}\n\n"
                        "If that is not possible, please contact help@pingcycle.org for assistance."
                    ),
                    chat_reference=from_id,
                )
            return existing_chat, False
        except core_models.Chat.DoesNotExist:
            print("This is an unlinked chat")

        # For unlinked chats, we expect uuid to be present
        # e.g. '/start c9bf9e57-1685-4c89-bafb-ff5af830be8a'
        if not attempting_to_link_chat:
            raise ValueError("Message does not start with '/start'")
        potential_uuid = message_text.split(" ", 1)[1]  # Get the part after '/start '
        linking_session = self._get_valid_linking_session(potential_uuid, from_id)

        with transaction.atomic():
            chat = linking_session.chat

            chat.state = core_models.Chat.State.ACTIVE

            chat.reference = from_id

            first_name = message_from.get("first_name", "").strip()
            last_name = message_from.get("last_name", "").strip()
            full_name = f"{first_name} {last_name}".strip()
            print(f"Setting chat name to: {full_name}")

            username = message_from.get("username")
            if username:
                number = f"@{username}"
            else:
                number = None

            chat.name = full_name
            chat.number = number

            chat.save(update_fields=["state", "reference", "name", "number"])

            return chat, True

    def _get_ref(self, data) -> Optional[str]:
        return data["message"]["message_id"]

    def _get_text(self, data):
        photo = data["message"].get("photo")

        if photo:
            return data["message"].get("caption")
        else:
            return data["message"].get("text")

    def send_message(self, message: core_models.Message):
        self._post_api(
            "sendMessage",
            chat_id=message.chat.reference,
            text=message.text,
            parse_mode="Markdown",
        )

    def _get_webhook_url(self):
        """
        Default get_webhook_url cannot be called during init due to circular import
        """
        return f"https://{WH_BASE_DOMAIN}/api/wh/messaging/TELEGRAM"

    def _setup_webhook(self):
        set_response = self._post_api(
            "setWebhook",
            url=self._get_webhook_url(),
            secret_token=self.webhook_secret,
        )
        print("TELEGRAM SET WEBHOOK RES: ", set_response)


PROVIDERS = {}

if core_models.Chat.Provider.TELEGRAM in CONFIG["MESSAGING_PROVIDERS"]:
    PROVIDERS[core_models.Chat.Provider.TELEGRAM] = Telegram()


def get_messaging_provider(provider_key) -> MessagingProvider:
    provider = PROVIDERS.get(provider_key)

    if provider is None:
        raise ValidationError({"provider": [f"Could not get provider: {provider_key}"]})

    return provider
