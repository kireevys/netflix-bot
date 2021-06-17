import logging
from abc import ABC
from time import sleep
from typing import Any, Optional

from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError, Unauthorized
from telegram.ext import Dispatcher, Updater
from typing import Iterable


logger = logging.getLogger()


class Mail(ABC):
    media: Any

    def build(self) -> dict:
        ...


class Sender(ABC):
    def send(self, message: Mail, recipient: Any) -> (bool, Optional[str]):
        ...


class TelegramSender(Sender):
    def __init__(self):
        self.bot = Bot(token=settings.BOT_TOKEN)

    def send(self, message: Mail, recipient: Any) -> (bool, Optional[str]):
        m = message.build()

        if message.media:
            self.bot.send_photo(chat_id=recipient, **m)
        else:
            self.bot.send_message(chat_id=recipient, *m)


class Builkmail:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.errors = 0

    def bulk(self, message: Mail, recipients: list, sender: Sender):
        logger.info("Start bulkmail", extra={"count": len(recipients)})
        for n, r in enumerate(recipients):
            if n % 30 == 0:
                sleep(0.005)

            try:
                sender.send(message, r.user_id)
            except Unauthorized:
                self.failed += 1
            except TelegramError:
                self.failed += 1

        logger.info(
            "Bulkmail has been end.",
            extra={"success": self.success, "failed": self.failed},
        )
