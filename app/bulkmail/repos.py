import logging
from typing import Iterable

from bulkmail.internal.core.message import Button, Media, Message
from bulkmail.internal.repositories import MessageRepository
from bulkmail.models import DjangoButton, DjangoMessage
from django.db.models import Q

logger = logging.getLogger("bulkmail")


def orm_to_core(orm_message: DjangoMessage) -> Message:
    buttons = [Button(link=i.link, text=i.text) for i in orm_message.buttons.all()]
    return Message(
        text=orm_message.text,
        media=Media(link=orm_message.media_link),
        buttons=buttons,
    )


class ORMMessageRepository(MessageRepository):
    def save(self, message: Message):
        buttons = [
            DjangoButton.objects.create(link=i.link, text=i.text)
            for i in message.buttons
        ]
        orm_message = DjangoMessage.objects.create(
            text=message.text, media_link=message.media.link
        )
        for b in buttons:
            orm_message.buttons.add(b)

        logger.info(f"Saved Message {orm_message.id}")

    def read(self, query: Q) -> Iterable[Message]:
        return list(map(orm_to_core, DjangoMessage.objects.filter(query)))
