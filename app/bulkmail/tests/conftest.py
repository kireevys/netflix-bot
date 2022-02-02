import pytest
from bulkmail.internal.core.message import Button, Media, Message


@pytest.fixture
def message() -> Message:
    message_text = "Some text"

    media_link = "https://example.com/static/pic.jpg"
    media_caption = "Message Media"
    media = Media(link=media_link, caption=media_caption)

    button_text = "button text"
    button_link = "http://example.com"
    buttons = [Button(text=button_text, link=button_link)]

    return Message(text=message_text, media=media, buttons=buttons)
