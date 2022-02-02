import json
from typing import List, TypedDict

from bulkmail.internal.core.message import Button, Media, Message


class MediaDict(TypedDict):
    caption: str
    link: str


class ButtonDict(TypedDict):
    text: str
    link: str


class MessageDict(TypedDict):
    text: str
    media: MediaDict
    buttons: List[ButtonDict]


def create_message_from_json(source: str) -> Message:
    as_dict: MessageDict = json.loads(source)
    return create_message_from_dict(as_dict)


def create_message_from_dict(source: MessageDict) -> Message:
    media = Media(**source["media"])
    buttons = [Button(**i) for i in source["buttons"]]
    return Message(text=source["text"], media=media, buttons=buttons)
