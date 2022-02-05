import datetime
from typing import List

import pytest
from bulkmail.internal.core.bulkmail import Bulkmail, BulkmailInfo
from bulkmail.internal.core.message import Button, Media, Message
from bulkmail.internal.core.recipient import Recipient, User


@pytest.fixture
def message() -> Message:
    message_text = "Some text"

    media_link = "https://example.com/static/pic.jpg"
    media = Media(link=media_link)

    buttons_d = [
        {"link": "http://example.com/", "text": "caption_1"},
        {"link": "http://example.com/", "text": "caption_2"},
    ]
    buttons = [Button(**i) for i in buttons_d]

    return Message(text=message_text, media=media, buttons=buttons)


@pytest.fixture
def bulkmail_info() -> BulkmailInfo:
    return BulkmailInfo(
        title="Title",
        created=datetime.datetime.now(),
        customer="Customer_name",
        price=10.5,
    )


@pytest.fixture
def recipients_list() -> List[Recipient]:
    return [Recipient(address=123, user=User(user_id=321))]


@pytest.fixture
def bulkmail(bulkmail_info, recipients_list, message) -> Bulkmail:
    return Bulkmail(
        message=message, recipients_list=recipients_list, info=bulkmail_info
    )
