import time
import random
from typing import Optional, Tuple, List, Dict

from pingcycle.tools.messaging_providers import MessagingProvider
import pingcycle.apps.core.models as core_models

# TODO: Retry logic??? yes!

# TELEGRAM RATE LIMITS
# 30 per second
# 1 per chat per second

# Add tests
# - correct mesages are being sent (with correct keywords) + products marked as sent
# - we stay within limits for many messages
# - we attempt to retry X times after Y seconds


class MessageSchedulerValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class MessageScheduler:
    """
    Sends messages in a way that does not violate a provider's rate limits

    Also responsible for retry logic
    """

    def __init__(self, provider: MessagingProvider):
        self.chat_limit, self.total_limit = self.set_limits(
            provider.CHAT_LIMIT_SECONDS, provider.TOTAL_LIMIT_SECONDS
        )
        self.last_sent_time_per_chat = {}  # Tracks last sent time per chat
        self.overall_messages_sent = (
            0  # Tracks overall messages sent in the current second
        )
        self.last_overall_check_time = time.time()
        self.max_retries = 3  # Maximum number of retries per message
        self.chat_queue = self._set_chat_queue()

    @staticmethod
    def set_limits(chat_limit, total_limit):
        """
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

        return normalized_chat_rate, normalized_total_rate

    def _set_chat_queue(self):
        products_chats_keywords = self._get_products_to_send()
        chat_queue = []

        for product, chats_keywords in products_chats_keywords:
            for chat, keywords in chats_keywords.items():
                chat_queue.append((product, chat, keywords, 0))  # Init retry count at 0

        return chat_queue

    def send_notified_products_in_queue(self):
        while self.chat_queue:
            current_time = time.time()

            # Reset overall message sent counter if a second has passed
            # TODO: This logic needs to change as per chat and overall
            # limnits may be different! here they are both 1 second...
            if current_time - self.last_overall_check_time > 1:
                self.overall_messages_sent = 0
                self.last_overall_check_time = current_time

            for i in range(len(self.chat_queue)):
                product, chat, keywords, retry_count = self.chat_queue.pop(0)
                last_sent_time = self.last_sent_time_per_chat.get(chat, 0)

                # Check per chat rate limit and overall rate limit
                # TODO: This logic needs to change as per chat and overall
                # limnits may be different! here they are both 1 second...
                if (current_time - last_sent_time >= 1) and (
                    self.overall_messages_sent < 30
                ):
                    successful = self._attempt_send(product, chat, keywords)
                    if successful:
                        # TODO: NotifiedProduct.Status.SENT needs to change!!
                        # we should track is all necessary chats were notified
                        # through Message.
                        # But when do we create the instances? Update db in bulk? Test...

                        # Updating here is wrong...
                        product.status = core_models.NotifiedProduct.Status.SENT
                        product.save(update_fields=["status"])

                        # Update tracking variables
                        self.last_sent_time_per_chat[chat] = current_time
                        self.overall_messages_sent += 1
                    else:
                        # Retry logic: increment retry count
                        retry_count += 1
                        if retry_count <= self.max_retries:
                            self.chat_queue.append(
                                (product, chat, keywords, retry_count)
                            )
                else:
                    # If not sent, return the item back to the queue
                    # TODO: We should prevent shuffling for ages!!!!!!! Test
                    self.chat_queue.append((product, chat, keywords))

                # Break after processing 30 messages per second overall
                if self.overall_messages_sent >= 30:
                    break

            # Sleep for a short time to prevent CPU over-usage and allow some time to pass
            time.sleep(0.01)

    def _attempt_send(self, product, chat, keywords):
        try:
            # Simulate potential network issues
            if random.choice([True, False]):
                raise Exception("Network issue occurred")

            print(
                f"Sent message for product {product} to chat {chat} with keywords {keywords}"
            )
            return True
        except Exception as e:
            print(f"Failed to send {product} to {chat}: {e}")
            return False

    def _get_products_to_send(
        self,
    ) -> List[
        Tuple[
            core_models.NotifiedProduct,
            Dict[core_models.Chat, List[core_models.Keyword]],
        ]
    ]:
        products = core_models.NotifiedProduct.objects.filter(
            status=core_models.NotifiedProduct.Status.QUEUED
        ).prefetch_related("keywords__user__chats")
        products_chats_keywords = []
        for product in products:
            chats_keywords = {}

            matched_keywords = product.keywords.all()
            for matched_keyword in matched_keywords:
                chats = matched_keyword.user.chats.all()

                for chat in chats:
                    if chat.state != core_models.Chat.State.ACTIVE:
                        continue
                    # Initialize the list if the user key doesn't exist
                    if chat not in chats_keywords:
                        chats_keywords[chat] = []
                    chats_keywords[chat].append(matched_keyword)

            if chats_keywords:
                products_chats_keywords.append((product, chats_keywords))

        return products_chats_keywords
