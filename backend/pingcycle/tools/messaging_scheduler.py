import time
import random
from typing import Optional, Tuple, List, Dict

from django.db import transaction

from config.settings import MAX_RETRIES_PER_MESSAGE
from pingcycle.tools.messaging_providers import MessagingProvider
import pingcycle.apps.core.models as core_models


class MessageSchedulerValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class MessageScheduler:
    """
    Sends messages in a way that does not violate a provider's rate limits

    Also responsible for retry logic
    """

    # TODO: Raising error for chat intervals should be on boot + test

    def __init__(self, provider: MessagingProvider):
        self.chat_provider = provider

        self.chat_interval, self.total_interval = self._set_intervals(
            provider.CHAT_LIMIT_SECONDS, provider.TOTAL_LIMIT_SECONDS
        )
        self.last_sent_time_per_chat = {}  # Tracks last sent time per chat
        self.last_overall_send_time = 0
        self.max_retries = (
            MAX_RETRIES_PER_MESSAGE  # Maximum number of retries per message
        )
        self.message_queue = self._set_message_queue()

    @staticmethod
    def _set_intervals(chat_limit, total_limit):
        """
        Sets how often a message could be sent

        Assumes limits are passed in a tuple (A, B) where
        A is number of messages and B is number of seconds

        The function normalise to per second and valdiates
        that per chat is below total limit
        """
        # Unpacking the (limit, period) tuples
        chat_rate, chat_period = chat_limit
        total_rate, total_period = total_limit

        # Normalize both rates to a per-second basis
        normalized_chat_rate = chat_rate / chat_period
        normalized_total_rate = total_rate / total_period

        if normalized_chat_rate > normalized_total_rate:
            raise MessageSchedulerValidationError(
                "Chat limit cannot be greater than total."
            )

        return 1 / normalized_chat_rate, 1 / normalized_total_rate

    def send_notified_products_in_queue(self):
        """
        Continuously loops through the message queue until it is empty.

        In each iteration, it checks whether the chat limit or the total
        limit has been exceeded.

        If the total limit is exceeded, the process waits before proceeding
        to the next iteration.

        If the chat limit is exceeded, the entry is re-added
        to the end of the queue.

        At the end of the loop, if there are entries left, it calculates
        the wait time based on the chat with the shortest remaining wait time.

        TODO: Could be further optimised
        e.g. Current flaw if there is 1 chat in the loop with 30 messages
        and we reach the limit we will only be able to wait after we have
        looped though the whole list with 29 items. Then, will hit the limit again
        and will only wait after looping through 28 items...
        """
        while len(self.message_queue) > 0:
            for _ in range(len(self.message_queue)):
                current_time = time.time()

                message = self.message_queue.pop(0)
                last_chat_time = self.last_sent_time_per_chat.get(message.chat, 0)

                chat_interval_passed = (
                    current_time - last_chat_time >= self.chat_interval
                )
                total_interval_passed = (
                    current_time - self.last_overall_send_time >= self.total_interval
                )

                if chat_interval_passed and total_interval_passed:
                    result = self._attempt_send(message)
                    if result["is_ok"]:
                        self._udpate_message_status(
                            message=message, status=core_models.Message.Status.SENT
                        )
                        self.last_sent_time_per_chat[message.chat] = result["time_sent"]
                        self.last_overall_send_time = result["time_sent"]
                    else:
                        message.retry_count += 1
                        if message.retry_count < self.max_retries:
                            # Return item back to the queue if below retry limit
                            self.message_queue.append(message)
                        else:
                            self._udpate_message_status(
                                message=message,
                                status=core_models.Message.Status.FAILED,
                                error_obj=result["error_obj"],
                            )
                        message.save(update_fields=["retry_count"])
                else:
                    # If not sent, return the item back to the queue
                    self.message_queue.append(message)
                    # Sleep if total limit exceeded
                    if not total_interval_passed:
                        time.sleep(
                            self.total_interval
                            - (current_time - self.last_overall_send_time)
                            + 0.01
                        )

            # Reached the end of the loop
            if len(self.message_queue) > 0:
                # Calculate the shortest wait time needed for the next action
                current_time = time.time()

                # The max function ensures that we do not calculate negative wait times.
                next_chat_intervals = [
                    max(
                        0,
                        (
                            self.chat_interval
                            - (
                                current_time
                                - self.last_sent_time_per_chat.get(message.chat, 0)
                            )
                        ),
                    )
                    for message in self.message_queue
                ]

                wait_time = min(next_chat_intervals)

                if wait_time > 0:
                    time.sleep(wait_time + 0.01)

    def _attempt_send(self, message) -> dict:
        try:
            return self.chat_provider.send_message(message)
        except Exception as e:
            # TODO: Should formatting be standardised into error object???
            return {
                "is_ok": False,
                "error_obj": {
                    "error_res_code": 500,
                    "error_msg": f"Internal error: {e}",
                },
            }

    def _set_message_queue(
        self,
    ) -> List[core_models.Message]:
        self._create_messages()

        messages = core_models.Message.objects.filter(
            status=core_models.Message.Status.CREATED,
            sender=core_models.Message.Sender.BOT,
        ).exclude(notified_product=None)

        return list(messages)

    def _create_messages(
        self,
    ):
        """
        Creates new messages in the database for any products that have
        state KEYWORDS_LINKED; and then sets state to MESSAGES_CREATED
        """
        with transaction.atomic():
            products = core_models.NotifiedProduct.objects.filter(
                state=core_models.NotifiedProduct.State.KEYWORDS_LINKED
            ).prefetch_related("keywords__user__chats")

            updated_products = []
            created_messages = []

            for product in products:
                chats_keywords = {}

                # TODO: REFACTOR!!!!
                matched_keywords = product.keywords.all()
                for matched_keyword in matched_keywords:
                    # Facilitates users having multiple chats
                    chats = matched_keyword.user.chats.all()

                    for chat in chats:
                        if chat.state != core_models.Chat.State.ACTIVE:
                            continue
                        # Initialize the list if the user key doesn't exist
                        if chat not in chats_keywords:
                            chats_keywords[chat] = []
                        chats_keywords[chat].append(matched_keyword.name)

                if chats_keywords:
                    for chat, keywords in chats_keywords.items():
                        message = core_models.Message(
                            notified_product=product,
                            chat=chat,
                            sender=core_models.Message.Sender.BOT,
                            text=product.get_formatted_message(users_keywrods=keywords),
                        )
                        created_messages.append(message)

                product.state = core_models.NotifiedProduct.State.MESSAGES_CREATED
                updated_products.append(product)

            core_models.Message.objects.bulk_create(created_messages)

            core_models.NotifiedProduct.objects.bulk_update(
                updated_products, fields=["state"]
            )

    @staticmethod
    def _udpate_message_status(
        message: core_models.Message,
        status: core_models.Message.Status,
        error_obj: Optional[dict] = None,
    ):
        message.status = status
        update_fields = ["status"]

        # Check if error_obj is provided and update if it is
        if error_obj is not None:
            message.error_res_code = error_obj["error_res_code"]
            message.error_msg = error_obj["error_msg"]
            update_fields.extend(["error_res_code", "error_msg"])

        message.save(update_fields=update_fields)
