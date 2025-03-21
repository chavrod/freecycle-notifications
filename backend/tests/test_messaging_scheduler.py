import time

import pytest

from pingcycle.tools.messaging_scheduler import MessageScheduler
import pingcycle.apps.core.models as core_models


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


# Mock the res of a send attempt
def message_send_res_success(*args, **kwargs):
    current_time = fake_time[0]
    # Increment new fake time and return the message set time
    fake_time[0] = current_time + 0.5
    return {"is_ok": True, "time_sent": current_time + 0.5}


TEST_SEND_MESSAGE_ERROR_RES_CODE = 400
TEST_SEND_MESSAGE_ERROR_RES_TEXT = "Test Error Text"


def message_send_res_error(*args, **kwargs):
    return {
        "is_ok": False,
        "error_obj": {
            "error_res_code": TEST_SEND_MESSAGE_ERROR_RES_CODE,
            "error_msg": TEST_SEND_MESSAGE_ERROR_RES_TEXT,
        },
    }


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
        message_scheduler, "_attempt_send", side_effect=message_send_res_success
    )

    mocker.patch.object(message_scheduler, "_udpate_message_status", return_value=True)

    # Create mock Message objects
    for i, number_of_messages in enumerate(chats_messages):
        chat_id = i + 1
        chat_mock = mocker.Mock(id=chat_id)
        for count in range(1, number_of_messages + 1):
            message_mock = mocker.Mock(id=count * chat_id)
            type(message_mock).chat = mocker.PropertyMock(return_value=chat_mock)
            message_scheduler.message_queue.append(message_mock)

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
        message_scheduler, "_attempt_send", side_effect=message_send_res_success
    )

    mocker.patch.object(message_scheduler, "_udpate_message_status", return_value=True)

    # Create mock Message objects
    for id in range(1, chats + 1):
        message_mock = mocker.Mock(id=id)
        chat_mock = mocker.Mock(id=id)
        type(message_mock).chat = mocker.PropertyMock(return_value=chat_mock)

        message_scheduler.message_queue.append(message_mock)

    # Record start time
    start_time = time.time()
    message_scheduler.send_notified_products_in_queue()
    end_time = time.time()

    elapsed_time = end_time - start_time
    # Check that the elapsed time is within expected bounds
    assert expected_min_time <= elapsed_time < expected_max_time


@pytest.mark.django_db
@pytest.mark.parametrize(
    "inputs, assert_messages",
    [
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [{"product_name": "apple pie", "external_id": 1}]
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                }
            ],
            id="1 Chat - 1KW linked to 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [{"product_name": "apple pie", "external_id": 1}],
                        "orange": [],
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                }
            ],
            id="1 Chat - 1KW linked to 1P + 1KW not linked",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [{"product_name": "apple pie", "external_id": 1}],
                        "orange": [
                            {
                                "product_name": "orange cake",
                                "external_id": 2,
                                "messages_scheduled": True,
                            }
                        ],
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                }
            ],
            id="1 Chat - 1KW linked to 1P + 1KW linked to 1P (with messages_scheduled == True)",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [{"product_name": "apple pie", "external_id": 1}],
                        "pie": [
                            {
                                "product_name": "apple pie",
                                "external_id": 1,
                            }
                        ],
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple", "pie"],
                    "status": core_models.Message.Status.SENT,
                }
            ],
            id="1 Chat - 2KW linked to 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                            {
                                "product_name": "apple watch",
                                "external_id": 2,
                            },
                        ],
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "apple watch",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="1 Chat - 1KW linked to 2P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [{"reference": "chat_1_user1"}],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                            {
                                "product_name": "apple cake",
                                "external_id": 2,
                            },
                        ],
                        "pie": [
                            {"product_name": "apple pie", "external_id": 1},
                        ],
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple", "pie"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "apple cake",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="1 Chat - 2KW linked to 1P + 1 same KW linked to other P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {"reference": "chat_1_user1"},
                        {"reference": "chat_2_user1"},
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_2_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (same user) - 1KW linked to 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {"reference": "chat_1_user1"},
                        {
                            "reference": "chat_2_user1",
                            "state": core_models.Chat.State.INACTIVE,
                        },
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                }
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (same user & 1 chat inactive) - 1KW linked to 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {"reference": "chat_1_user1"},
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                },
                {
                    "username": "user2",
                    "chats": [
                        {"reference": "chat_1_user2"},
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                },
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user2",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (different users) - each with 1KW linked to same 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {"reference": "chat_1_user1"},
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                },
                {
                    "username": "user2",
                    "chats": [
                        {"reference": "chat_1_user2"},
                    ],
                    "keywords_products": {
                        "cake": [
                            {"product_name": "orange cake", "external_id": 2},
                        ]
                    },
                },
            ],
            [
                {
                    "product_name": "apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "orange cake",
                    "chat_reference": "chat_1_user2",
                    "linked_keywords": ["cake"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (different users) - each with 1KW linked to different 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {
                            "reference": "chat_1_user1",
                            "state": core_models.Chat.State.INACTIVE,
                        },
                    ],
                    "keywords_products": {
                        "apple": [
                            {"product_name": "apple pie", "external_id": 1},
                        ]
                    },
                },
                {
                    "username": "user2",
                    "chats": [
                        {"reference": "chat_1_user2"},
                    ],
                    "keywords_products": {
                        "cake": [
                            {"product_name": "orange cake", "external_id": 2},
                        ]
                    },
                },
            ],
            [
                {
                    "product_name": "orange cake",
                    "chat_reference": "chat_1_user2",
                    "linked_keywords": ["cake"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (different users) - each with 1KW linked to different 1P",
        ),
        pytest.param(
            [
                {
                    "username": "user1",
                    "chats": [
                        {
                            "reference": "chat_1_user1",
                        },
                    ],
                    "keywords_products": {
                        "apple": [
                            {
                                "product_name": "hot apple pie",
                                "external_id": 1,
                            },
                        ],
                        "pie": [
                            {
                                "product_name": "hot apple pie",
                                "external_id": 1,
                            },
                        ],
                        "jam": [
                            {"product_name": "hot banana with jam", "external_id": 2},
                        ],
                    },
                },
                {
                    "username": "user2",
                    "chats": [
                        {"reference": "chat_1_user2"},
                    ],
                    "keywords_products": {
                        "hot": [
                            {
                                "product_name": "hot apple pie",
                                "external_id": 1,
                            },
                            {"product_name": "hot banana with jam", "external_id": 2},
                        ],
                        "apple": [
                            {
                                "product_name": "hot apple pie",
                                "external_id": 1,
                            },
                        ],
                        "pie": [
                            {
                                "product_name": "hot apple pie",
                                "external_id": 1,
                            },
                        ],
                        "banana": [
                            {"product_name": "hot banana with jam", "external_id": 2},
                        ],
                    },
                },
            ],
            [
                {
                    "product_name": "hot apple pie",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["apple", "pie"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "hot apple pie",
                    "chat_reference": "chat_1_user2",
                    "linked_keywords": ["hot", "apple", "pie"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "hot banana with jam",
                    "chat_reference": "chat_1_user1",
                    "linked_keywords": ["jam"],
                    "status": core_models.Message.Status.SENT,
                },
                {
                    "product_name": "hot banana with jam",
                    "chat_reference": "chat_1_user2",
                    "linked_keywords": ["hot", "banana"],
                    "status": core_models.Message.Status.SENT,
                },
            ],
            id="2 Chats (different users) - variation with many Ps and KWs",
        ),
    ],
)
def test_messages_created(
    inputs,
    assert_messages,
    get_or_create_user_chats_keywords_products,
    mocker,
):
    """
    This is an integration test to see how many messages get sent,
    based on number of products, linked keywords, and chats.

    Scenarios

    1 Chat - 1KW linked to 1P
    1 Chat - 1KW linked to 1P + 1KW not linked
    1 Chat - 1KW linked to 1P + 1KW linked to 1P (with messages_scheduled == True)
    1 Chat - 2KW linked to 1P
    1 Chat - 1KW linked to 2P
    1 Chat - 2KW linked to 1P + 1 same KW linked to other P

    2 Chats (same user) - 1KW linked to 1P
    2 Chats (same user & 1 chat inactive) - 1KW linked to 1P
    2 Chats (different users) - each with 1KW linked to same 1P
    2 Chats (different users) - each with 1KW linked to different 1P
    2 Chats (different users & 1 chat inactive) - each with 1KW linked different 1P

    2 Chats (different users) - variation with many Ps and KWs
    """
    # ARRANGE

    # Create db objects
    for input in inputs:
        get_or_create_user_chats_keywords_products(
            input["username"], input["chats"], input["keywords_products"]
        )

    mock_provider = MockMessagingProvider((1000, 1), (2000, 1))
    message_scheduler = MessageScheduler(provider=mock_provider)

    mocker.patch.object(
        message_scheduler, "_attempt_send", side_effect=message_send_res_success
    )

    # ACT
    message_scheduler.send_notified_products_in_queue()

    # ASSERT

    # Assert all product statues have been updated
    notified_products_without_scheduled_msg_count = (
        core_models.NotifiedProduct.objects.filter(messages_scheduled=False)
    )
    assert (
        notified_products_without_scheduled_msg_count.count() == 0
    ), "Expected all products to have scheduled messages"

    # Assert all messages have been sent
    sent_messages_count = core_models.Message.objects.filter(
        status=core_models.Message.Status.SENT
    ).count()

    assert sent_messages_count == len(
        assert_messages
    ), f"Expected {len(assert_messages)} to be sent, but sent {sent_messages_count}"

    all_messages_dict = {
        f"{m.notified_product.product_name}_{m.chat.reference}": m
        for m in core_models.Message.objects.all()
        .select_related("notified_product")
        .select_related("chat")
    }

    # Per message assertions
    for assert_message in assert_messages:
        # Find message
        message_lookup = (
            f"{assert_message['product_name']}_{assert_message['chat_reference']}"
        )
        message = all_messages_dict.get(message_lookup)
        assert (
            message is not None
        ), f"Expected to have message with chat ref: {assert_message['chat_reference']} and linked to product: {assert_message['product_name']}"

        # Assert message status
        assert (
            message.status == assert_message["status"]
        ), f"Expected message to have status {assert_message['status']}"

        # Check for the presence of the linked keywords in message text
        message_text = message.text
        marker = "Linked Keywords:"
        marker_index = message_text.index(marker)
        keywords_in_text = message_text[marker_index + len(marker) :].strip()
        keywords_list = [kw.strip() for kw in keywords_in_text.split(",")]

        for keyword in assert_message["linked_keywords"]:
            assert (
                keyword in keywords_list
            ), f"Expected {keyword} to be present in the message text"
            keywords_list.remove(keyword)
        # Final assertion to ensure keywords_list is empty
        assert not keywords_list, "Expected all keywords to be removed from the list"

        all_messages_dict.pop(message_lookup)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "max_retries, number_of_fail_attmepts, assert_message",
    [
        pytest.param(
            3,
            3,
            {
                "status": core_models.Message.Status.FAILED,
                "retry_count": 3,
                "error_res_code": TEST_SEND_MESSAGE_ERROR_RES_CODE,
                "error_msg": TEST_SEND_MESSAGE_ERROR_RES_TEXT,
            },
            id="Failed Mesage",
        ),
        pytest.param(
            3,
            2,
            {
                "status": core_models.Message.Status.SENT,
                "retry_count": 2,
                "error_res_code": None,
                "error_msg": None,
            },
            id="Succeed With Retries",
        ),
        pytest.param(
            3,
            0,
            {
                "status": core_models.Message.Status.SENT,
                "retry_count": 0,
                "error_res_code": None,
                "error_msg": None,
            },
            id="Succeed No Retries",
        ),
    ],
)
def test_retry_on_fail(
    max_retries,
    number_of_fail_attmepts,
    assert_message,
    get_or_create_user_chats_keywords_products,
    mocker,
):
    """
    Create 1 keywrod with 1 Product and adjust the message send response
    """
    # ARRANGE

    get_or_create_user_chats_keywords_products()

    mocker.patch(
        "pingcycle.tools.messaging_scheduler.MAX_RETRIES_PER_MESSAGE", new=max_retries
    )

    mock_provider = MockMessagingProvider((1000, 1), (2000, 1))
    message_scheduler = MessageScheduler(provider=mock_provider)

    mocked_responses = []
    for _ in range(number_of_fail_attmepts):
        mocked_responses.append(message_send_res_error())
    mocked_responses.append(message_send_res_success())

    mocker.patch.object(
        message_scheduler, "_attempt_send", side_effect=mocked_responses
    )

    # ACT
    message_scheduler.send_notified_products_in_queue()

    # ASSERT

    # Assert number of messages
    all_messages = core_models.Message.objects.all()
    assert all_messages.count() == 1, "Expected to only have 1 message"

    message = all_messages.first()

    assert (
        message.status == assert_message["status"]
    ), f"Expected message status to be {assert_message['status']}"
    assert (
        message.retry_count == assert_message["retry_count"]
    ), f"Expected message retry_count to be {assert_message['retry_count']}"
    assert (
        message.error_res_code == assert_message["error_res_code"]
    ), f"Expected message error_res_code to be {assert_message['error_res_code']}"
    assert (
        message.error_msg == assert_message["error_msg"]
    ), f"Expected message error_msg to be {assert_message['error_msg']}"
