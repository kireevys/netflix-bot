import datetime
import json
from typing import List, TypedDict

from bulkmail.internal.core.bulkmail import Bulkmail, BulkmailInfo
from bulkmail.internal.core.message import Button, Media, Message
from bulkmail.repos import Filters, ORMMessageRepository, ORMRecipientRepository
from django.db.models import Q


class MediaDict(TypedDict):
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


def build_bulkmail_from_dict(
    message_id: int, recipient_filter: Filters, info: dict
) -> Bulkmail:
    message = ORMMessageRepository().read(Q(pk=message_id))
    recipients = ORMRecipientRepository().read(recipient_filter)
    info = BulkmailInfo(created=datetime.datetime.now(), **info)

    return Bulkmail(message[0], recipients_list=recipients, info=info)
