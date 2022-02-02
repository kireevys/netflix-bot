from bulkmail.internal.core.message import Message
from bulkmail.internal.repositories import MessageRepository
from bulkmail.models import DjangoButton, DjangoMessage


class ORMMessageRepository(MessageRepository):
    def save(self, message: Message):
        buttons = [
            DjangoButton.objects.create(link=i.link, text=i.text)
            for i in message.buttons
        ]
        d = DjangoMessage.objects.create(
            text=message.text, media_link=message.media.link
        )
        for b in buttons:
            d.buttons.add(b)
