from bulkmail.internal.core.message import Message
from bulkmail.internal.repositories import MessageRepository
from bulkmail.models import DjangoMessage
from bulkmail.repos import ORMMessageRepository


def test_save_success(db, message: Message):
    repository = ORMMessageRepository()
    assert isinstance(repository, MessageRepository)

    repository.save(message)

    django_message: DjangoMessage = DjangoMessage.objects.first()

    assert django_message.text == message.text
    assert django_message.media_link == message.media.link

    f_button, s_button = django_message.buttons.all()

    assert f_button.link == message.buttons[0].link
    assert f_button.text == message.buttons[0].text

    assert s_button.link == message.buttons[1].link
    assert s_button.text == message.buttons[1].text


def test_save_without_buttons(db, message: Message):
    repository = ORMMessageRepository()

    message.buttons = []

    repository.save(message)

    django_message: DjangoMessage = DjangoMessage.objects.first()

    assert django_message.text == message.text
    assert django_message.media_link == message.media.link

    assert len(django_message.buttons.all()) == 0


def test_save_with_invalid_url_by_media(db, message):
    repository = ORMMessageRepository()

    message.media.link = "BROKEN_LINK"
    # Нет валидатора на поле URLField. Оставлю пока так, не уверен, что оно мне надо
    repository.save(message)
