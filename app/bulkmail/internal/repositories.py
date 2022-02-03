from abc import ABC, abstractmethod
from typing import Any, Iterable, List

from bulkmail.internal.core.message import Message
from bulkmail.internal.core.recipient import Recipient


class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message):
        ...

    @abstractmethod
    def read(self, query: Any) -> Iterable[Message]:
        ...


class RecipientRepository(ABC):
    @abstractmethod
    def read(self, query: Any) -> List[Recipient]:
        ...
