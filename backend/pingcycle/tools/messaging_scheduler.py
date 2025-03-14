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
# - we stay within limits for many messages
# - we attempt to retry X times after Y seconds
# - correct mesages are being sent (with correct keywords) + products marked as sent


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
        self.chat_interval, self.total_interval = self._set_intervals(
            provider.CHAT_LIMIT_SECONDS, provider.TOTAL_LIMIT_SECONDS
        )
        self.last_sent_time_per_chat = {}  # Tracks last sent time per chat
        self.last_overall_send_time = 0
        self.max_retries = 3  # Maximum number of retries per message
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

    def _set_message_queue(self):
        products_chats_keywords = self._get_products_to_send()
        message_queue = []

        for product, chats_keywords in products_chats_keywords:
            for chat, keywords in chats_keywords.items():
                message_queue.append(
                    (product, chat, keywords, 0)
                )  # Init retry count at 0

        return message_queue

    def send_notified_products_in_queue(self):
        while len(self.message_queue) > 0:
            for i in range(len(self.message_queue)):
                current_time = time.time()

                product, chat, keywords, retry_count = self.message_queue.pop(0)
                last_chat_time = self.last_sent_time_per_chat.get(chat, 0)

                print("current_time: ", current_time)
                print("last_chat_time: ", last_chat_time)
                print("last_overall_send_time : ", self.last_overall_send_time)
                print("time passed: ", current_time - last_chat_time)
                print("total_interval: ", self.total_interval)
                chat_interval_passed = (
                    current_time - last_chat_time >= self.chat_interval
                )
                total_interval_passed = (
                    current_time - self.last_overall_send_time >= self.total_interval
                )
                print(chat_interval_passed, total_interval_passed)

                if chat_interval_passed and total_interval_passed:
                    print("Sending...")
                    time_sent = self._attempt_send(product, chat, keywords)
                    if time_sent:
                        self._udpate_message_status()
                        self.last_sent_time_per_chat[chat] = time_sent
                        self.last_overall_send_time = time_sent
                    else:
                        retry_count += 1
                        if retry_count <= self.max_retries:
                            self.message_queue.append(
                                (product, chat, keywords, retry_count)
                            )
                        else:
                            self._udpate_message_status()
                else:
                    print("Sleeping...")
                    # If not sent, return the item back to the queue
                    self.message_queue.append((product, chat, keywords, retry_count))
                    # Sleep if total limit exceeded
                    if not total_interval_passed:
                        time.sleep(
                            self.total_interval
                            - (current_time - self.last_overall_send_time)
                        )

            # Reached the end of the loop
            print(
                "Reached the end of the loop with queue length: ",
                len(self.message_queue),
            )
            if len(self.message_queue) > 0:
                print("Getting valid wait time...")
                print("self.message_queue: ", self.message_queue)
                # Calculate the shortest wait time needed for the next action
                current_time = time.time()

                # The max function ensures that we do not calculate negative wait times.
                next_chat_intervals = [
                    max(
                        0,
                        (
                            self.chat_interval
                            - (current_time - self.last_sent_time_per_chat.get(chat, 0))
                        ),
                    )
                    for _, chat, _, _ in self.message_queue
                ]
                print("next_chat_intervals: ", next_chat_intervals)

                wait_time = min(next_chat_intervals)
                print("wait_time chat: ", wait_time)

                if wait_time > 0:
                    time.sleep(wait_time)

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

    @staticmethod
    def _udpate_message_status(message, status):
        pass
        # TODO: ...pre-create messages.. Update db in bulk? Test...
        # product.status = core_models.NotifiedProduct.Status.SENT
        # product.save(update_fields=["status"])
