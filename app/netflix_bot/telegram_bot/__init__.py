from functools import cached_property

from django.conf import settings
from telegram import Bot, User


class CurrentBot():
    @cached_property
    def get(self) -> User:
        return Bot(settings.BOT_TOKEN).get_me()


ME = CurrentBot()
