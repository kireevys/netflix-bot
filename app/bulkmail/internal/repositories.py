from abc import ABC, abstractmethod

from bulkmail.internal.core.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message):
        ...
