from bulkmail.internal.core.message import Message
from bulkmail.internal.repositories import MessageRepository
from bulkmail.models import DjangoButton, DjangoMessage
from bulkmail.repos import ORMMessageRepository, orm_to_core
from django.db.models import Q


def test_read(db, message: Message):
    repository = ORMMessageRepository()
    assert isinstance(repository, MessageRepository)

    DjangoMessage.objects.create(text=message.text, media_link=message.media.link)

    query = Q(pk=1)
    actual = repository.read(query)

    assert len(actual) == 1
    assert isinstance(actual[0], Message)


def test_orm_to_core(db, message: Message):
    buttons = [
        DjangoButton.objects.create(link=i.link, text=i.text) for i in message.buttons
    ]
    dm = DjangoMessage.objects.create(text=message.text, media_link=message.media.link)
    list(map(dm.buttons.add, buttons))

    dm.refresh_from_db()

    result = orm_to_core(dm)

    assert result == message
