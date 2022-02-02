import pytest
from bulkmail.core.message import Button, Media, Message


def test_create_message():
    message_text = "Some text"

    media_link = "https://example.com/static/pic.jpg"
    media_caption = "Message Media"
    media = Media(link=media_link, caption=media_caption)

    button_text = "button text"
    button_link = "http://example.com"
    buttons = [Button(text=button_text, link=button_link)]

    message = Message(text=message_text, media=media, buttons=buttons)

    assert message.text == message_text
    assert message.media == media
    assert len(message.buttons) == len(buttons)
    assert message.buttons == buttons


@pytest.mark.parametrize(
    "first_buttons, second_buttons",
    [
        (
            [
                {"link": "http://example.com/", "text": "caption_1"},
                {"link": "http://example.com/", "text": "caption_2"},
            ],
            [
                {"link": "http://example.com/", "text": "caption_1"},
                {"link": "http://example.com/", "text": "caption_2"},
            ],
        ),
        (
            [
                {"link": "http://example.com/", "text": "caption_1"},
                {"link": "http://example.com/", "text": "caption_2"},
            ],
            [
                {"link": "http://example.com/", "text": "caption_2"},
                {"link": "http://example.com/", "text": "caption_1"},
            ],
        ),
        (
            [],
            [],
        ),
    ],
    ids=["Same order", "Wrong order", "Has not buttons"],
)
def test_message_equal(first_buttons, second_buttons):
    dict_media = {"link": "http://example.com/static/pic_1.jpg", "caption": "caption"}
    message_text = "Some text"
    dict_message_first = {
        "text": message_text,
        "media": Media(**dict_media),
        "buttons": [Button(**i) for i in first_buttons],
    }
    dict_message_second = {
        "text": message_text,
        "media": Media(**dict_media),
        "buttons": [Button(**i) for i in second_buttons],
    }

    assert Message(**dict_message_first) == Message(**dict_message_second)


@pytest.mark.parametrize(
    "first, second",
    [
        (
            {
                "text": "Not equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_1"),
                    Button(link="http://example.com/", text="caption_2"),
                ],
            },
            {
                "text": "Bla-Bla",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_1"),
                    Button(link="http://example.com/", text="caption_2"),
                ],
            },
        ),
        (
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="Not equal",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_1"),
                    Button(link="http://example.com/", text="caption_2"),
                ],
            },
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_1"),
                    Button(link="http://example.com/", text="caption_2"),
                ],
            },
        ),
        (
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_1"),
                    Button(link="http://example.com/", text="caption_2"),
                ],
            },
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_0"),
                    Button(link="http://example.com/", text="caption_1"),
                ],
            },
        ),
        (
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [],
            },
            {
                "text": "Equal",
                "media": Media(
                    link="http://example.com/static/pic_1.jpg",
                    caption="caption",
                ),
                "buttons": [
                    Button(link="http://example.com/", text="caption_0"),
                    Button(link="http://example.com/", text="caption_1"),
                ],
            },
        ),
    ],
    ids=[
        "By text",
        "By media",
        "By buttons",
        "Different count buttons",
    ],
)
def test_message_not_equal(first: dict, second: dict):
    assert Message(**first) != Message(**second)
