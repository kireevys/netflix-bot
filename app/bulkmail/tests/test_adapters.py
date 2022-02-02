import json
from typing import List

from bulkmail.internal.adapters import (
    ButtonDict,
    MediaDict,
    create_message_from_dict,
    create_message_from_json,
)
from bulkmail.internal.core.message import Button, Media, Message


def test_create_message_from_dict():
    message_text = "Some text"
    dict_media = {
        "link": "http://example.com/static/pic_1.jpg",
        "caption": "caption",
    }
    dict_buttons: List[dict] = [
        {"link": "http://example.com/", "text": "caption_1"},
        {"link": "http://example.com/", "text": "caption_2"},
    ]
    dict_message = {
        "text": message_text,
        "media": dict_media,
        "buttons": dict_buttons,
    }
    expected = Message(
        text=message_text,
        media=Media(**dict_media),
        buttons=[Button(**i) for i in dict_buttons],
    )

    actual = create_message_from_dict(source=dict_message)

    assert actual == expected


def test_create_message_from_json():
    message_text = "Some text"
    dict_media = MediaDict(
        link="http://example.com/static/pic_1.jpg",
        caption="caption",
    )
    dict_buttons: List[dict] = [
        ButtonDict(link="http://example.com/", text="caption_1"),
        ButtonDict(link="http://example.com/", text="caption_2"),
    ]
    dict_message = {
        "text": message_text,
        "media": dict_media,
        "buttons": dict_buttons,
    }
    expected = Message(
        text=message_text,
        media=Media(**dict_media),
        buttons=[Button(**i) for i in dict_buttons],
    )
    json_message = json.dumps(dict_message)

    actual = create_message_from_json(source=json_message)

    assert actual == expected
