from bulkmail.internal.core.message import Message


class MessageRepository:
    def save(self, message: Message):
        ...


def test_save(message: Message):
    repository = MessageRepository()
    repository.save(message)
