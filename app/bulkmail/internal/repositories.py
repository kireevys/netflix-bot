from abc import ABC, abstractmethod
from typing import Any, Iterable

from bulkmail.internal.core.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message):
        ...

    @abstractmethod
    def read(self, query: Any) -> Iterable[Message]:
        ...
