"""
Test 1: Per chat Limit test_chat_limit_enforce

  Case 1:
    Chat input:
      1 chat with 30 messages (products) per chat
    Limits:
      Chat Limit is 1 per second
      Total Limit is 30 per second
    Assertion
      Takes over 30 seconds and under 60 seconds to send all messages

  Case 2
    Chat input:
      1 chat with 30 messages (products) per chat
    Limits:
      Chat Limit is 2 per second
      Total Limit is 30 per second
    Assertion
      Takes over 60 seconds and under 120 seconds to send all messages

  Case 3
    Chat input:
      1st chat with 30 messages (products) per chat
      2nd chat with 30 messages (products) per chat
    Limits:
      Chat Limit is 1 per second
      Total Limit is 30 per second
    Assertion
      Takes over 30 seconds and under 60 seconds to send all messages

test 1
 -> Chat Limit is 1 per second
 -> Total Limit is 30 per second
 Assert it takes over
 test 2
->
"""

import time

import pytest

from pingcycle.tools.messaging_scheduler import MessageScheduler


# Define a mock MessagingProvider for testing purposes
class MockMessagingProvider:
    def __init__(self, chat_limit, total_limit):
        self.CHAT_LIMIT_SECONDS = chat_limit
        self.TOTAL_LIMIT_SECONDS = total_limit


# Mock the timestamp
fake_time = [100]


def get_fake_time():
    return fake_time[0]


def increment_fake_time(amount):
    fake_time[0] += amount
    return fake_time[0]


# Mock the send attempt as always successful
def successful_send_time(*args, **kwargs):
    current_time = fake_time[0]
    # Increment new fake time and return the message set time
    fake_time[0] = current_time + 0.5
    return {"is_ok": True, "time_sent": current_time + 0.5}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "chat_limit, chats_messages, expected_min_time, expected_max_time",
    [
        pytest.param((1, 1), [30], 30, 60, id="1 Chat with 1 message per second"),
        pytest.param((1, 2), [30], 60, 120, id="1 Chat with 1 message per 2 seconds"),
        pytest.param((1, 1), [30, 30], 30, 60, id="2 Chat with 1 message per second"),
    ],
)
def test_individual_chat_limit_enforce(
    chat_limit,
    chats_messages,
    expected_min_time,
    expected_max_time,
    mocker,
):
    """
    The primary objective of this test is to determine the minimum time
    required to send all messages given the chat limits. The total limit is set
    high to ensure it does not interfere with the testing process. We assume that
    it takes 0.5 seconds to send each message.
    """
    # Execute helper setup
    mock_provider = MockMessagingProvider(chat_limit, (1000, 1))
    message_scheduler = MessageScheduler(provider=mock_provider)

    # Mock to replace time.time() and control time progression
    mocker.patch("time.time", side_effect=get_fake_time)
    mocker.patch("time.sleep", side_effect=increment_fake_time)

    mocker.patch.object(
        message_scheduler, "_attempt_send", side_effect=successful_send_time
    )

    mocker.patch.object(message_scheduler, "_udpate_message_status", return_value=True)

    # Create mock objects for product, chat, and keywords using mocker
    keywords_mock = [mocker.Mock(id=2)]

    for i, number_of_messages in enumerate(chats_messages):
        chat_id = i + 1
        chat_mock = mocker.Mock(id=chat_id)
        for count in range(1, number_of_messages + 1):
            message_scheduler.message_queue.append(
                (mocker.Mock(id=chat_id + count), chat_mock, keywords_mock, 0)
            )

    # Record start time
    start_time = time.time()
    message_scheduler.send_notified_products_in_queue()
    end_time = time.time()

    elapsed_time = end_time - start_time
    # Check that the elapsed time is within expected bounds
    assert expected_min_time <= elapsed_time < expected_max_time


@pytest.mark.django_db
@pytest.mark.parametrize(
    "total_limit, chats, expected_min_time, expected_max_time",
    # NOTE: When calculating expected_min_time, we need to also account for
    # the fact that it takes 0.5 seconds to send each message...
    [
        pytest.param((30, 1), 30, 15, 20, id="30 Chats with 30 messages per second"),
        pytest.param((1, 1), 30, 40, 50, id="30 Chats with 1 messages per second"),
    ],
)
def test_total_chat_limit_enforce(
    total_limit,
    chats,
    expected_min_time,
    expected_max_time,
    mocker,
):
    """
    In this scenario, we have multiple chats, and we're examining how
    changing the total limit impacts the overall time required. The
    chat limit is set to allow 1 message per second, and for simplicity,
    each chat only has 1 message to be sent. We assume it takes 0.5
    seconds to send a message.
    """
    # Execute helper setup
    mock_provider = MockMessagingProvider((1, 1), total_limit)
    message_scheduler = MessageScheduler(provider=mock_provider)

    # Mock and control time progression
    mocker.patch("time.time", side_effect=get_fake_time)
    mocker.patch("time.sleep", side_effect=increment_fake_time)

    mocker.patch.object(
        message_scheduler, "_attempt_send", side_effect=successful_send_time
    )

    mocker.patch.object(message_scheduler, "_udpate_message_status", return_value=True)

    # Create mock objects for product, chat, and keywords using mocker
    keywords_mock = [mocker.Mock(id=2)]

    for id in range(1, chats + 1):
        message_mock = mocker.Mock(id=id)
        chat_mock = mocker.Mock(id=id)
        type(message_mock).chat = mocker.PropertyMock(return_value=chat_mock)

        message_scheduler.message_queue.append((message_mock, 0))

    # Record start time
    start_time = time.time()
    message_scheduler.send_notified_products_in_queue()
    end_time = time.time()

    elapsed_time = end_time - start_time
    # Check that the elapsed time is within expected bounds
    assert expected_min_time <= elapsed_time < expected_max_time


@pytest.mark.django_db
@pytest.mark.parametrize(
    "chat_limit, chats_messages, expected_min_time, expected_max_time",
    [
        pytest.param((1, 1), [30], 30, 60, id="1 Chat with 1 message per second"),
        pytest.param((1, 2), [30], 60, 120, id="1 Chat with 1 message per 2 seconds"),
        pytest.param((1, 1), [30, 30], 30, 60, id="2 Chat with 1 message per second"),
    ],
)
def test_retry_limit_enforce(
    chat_limit,
    chats_messages,
    expected_min_time,
    expected_max_time,
    mocker,
):
    """
    The primary objective of this test is to determine the minimum time
    required to send all messages given the chat limits. The total limit is set
    high to ensure it does not interfere with the testing process. We assume that
    it takes 0.5 seconds to send each message.
    """
    # Execute helper setup
    mock_provider = MockMessagingProvider(chat_limit, (1000, 1))
    message_scheduler = MessageScheduler(provider=mock_provider)

    # Mock to replace time.time() and control time progression
    mocker.patch("time.time", side_effect=get_fake_time)
    mocker.patch("time.sleep", side_effect=increment_fake_time)

    mocker.patch.object(
        message_scheduler, "_attempt_send", side_effect=successful_send_time
    )

    mocker.patch.object(message_scheduler, "_udpate_message_status", return_value=True)

    # Create mock objects for product, chat, and keywords using mocker
    keywords_mock = [mocker.Mock(id=2)]

    for i, number_of_messages in enumerate(chats_messages):
        chat_id = i + 1
        chat_mock = mocker.Mock(id=chat_id)
        for count in range(1, number_of_messages + 1):
            message_scheduler.message_queue.append(
                (mocker.Mock(id=chat_id + count), chat_mock, keywords_mock, 0)
            )

    # Record start time
    start_time = time.time()
    message_scheduler.send_notified_products_in_queue()
    end_time = time.time()

    elapsed_time = end_time - start_time
    # Check that the elapsed time is within expected bounds
    assert expected_min_time <= elapsed_time < expected_max_time
