import pytest
from bulkmail.internal.core.message import Button, Media, Message


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
