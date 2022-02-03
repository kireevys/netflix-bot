import logging
from enum import Enum
from typing import Iterable, List

from bulkmail.internal.core.message import Button, Media, Message
from bulkmail.internal.core.recipient import Recipient, User
from bulkmail.internal.repositories import MessageRepository, RecipientRepository
from bulkmail.models import DjangoButton, DjangoMessage, DjangoRecipient
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


class Filters(Enum):
    ANY = "ANY"
    TEST = "TEST"


class ORMRecipientRepository(RecipientRepository):
    Filters = Filters

    def _orm_to_core(self, d_recipient: DjangoRecipient) -> Recipient:
        return Recipient(address=d_recipient.user.user_id, user=User(d_recipient.pk))

    def read(self, query: Filters) -> List[Recipient]:
        if query != Filters.ANY:
            return [
                self._orm_to_core(i)
                for i in DjangoRecipient.objects.filter(user__usertag__tag=query.value)
            ]
        else:
            return [self._orm_to_core(i) for i in DjangoRecipient.objects.all()]
