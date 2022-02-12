import logging
from enum import Enum
from typing import List

from bulkmail.internal.core.bulkmail import Bulkmail
from bulkmail.internal.core.message import Button, Media, Message
from bulkmail.internal.core.recipient import Recipient
from bulkmail.internal.repositories import (
    BulkmailRepository,
    MessageRepository,
    RecipientRepository,
)
from bulkmail.models import DjangoBulkmail, DjangoMessage, Envelope
from django.db.models import Q
from netflix_bot.models import User

logger = logging.getLogger("bulkmail")


def orm_to_core(orm_message: DjangoMessage) -> Message:
    buttons = [
        Button(link=i.link, text=i.text) for i in orm_message.djangobutton_set.all()
    ]
    return Message(
        text=orm_message.text,
        media=Media(link=orm_message.media_link),
        buttons=buttons,
    )


class ORMMessageRepository(MessageRepository):
    def read(self, query: Q) -> List[Message]:
        return list(map(orm_to_core, DjangoMessage.objects.filter(query)))


class Filters(Enum):
    ANY = "ANY"
    TEST = "TEST"


class ORMRecipientRepository(RecipientRepository):
    Filters = Filters

    @staticmethod
    def _orm_to_core(d_recipient: User) -> Recipient:
        return Recipient(address=d_recipient.user_id)

    def read(self, query: Filters) -> List[Recipient]:
        if query != Filters.ANY:
            return [
                self._orm_to_core(i)
                for i in User.objects.filter(usertag__tag=query.value)
            ]
        else:
            return [self._orm_to_core(i) for i in User.objects.all()]


class ORMBulkmailRepository(BulkmailRepository):
    def save(self, bulkmail: Bulkmail):
        d_bulkmail = DjangoBulkmail.objects.create(
            title=bulkmail.info.title,
            customer=bulkmail.info.customer,
            price=bulkmail.info.price,
        )
        [
            Envelope.objects.create(
                bulkmail=d_bulkmail,
                text=bulkmail.message.text,
                media=bulkmail.message.media.link,
                keyboard=[
                    {"link": i.link, "text": i.text} for i in bulkmail.message.buttons
                ],
                user=User.objects.get(user_id=r.address),
            )
            for r in bulkmail.recipients_list
        ]

    def read(self, query: Q) -> List[Bulkmail]:
        result = DjangoBulkmail.objects.filter(query)
        answer = []
        for b in result:
            envelope: Envelope = b.envelope_set.first()
            recipients = [
                Recipient(address=r.user.user_id) for r in b.envelope_set.all()
            ]
            message = Message(
                text=envelope.text,
                media=Media(envelope.media),
                buttons=envelope.buttons,
            )
            bm = Bulkmail(
                message=message,
                recipients_list=recipients,
                info=b.bulkmail_info,
            )
            answer.append(bm)

        return answer
