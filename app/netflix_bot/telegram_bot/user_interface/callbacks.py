import logging
from abc import ABC
from time import time

from django.conf import settings
from netflix_bot.telegram_bot.senders import Sender
from netflix_bot.telegram_bot.user_interface.router import Router
from telegram import (
    Bot,
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMedia,
    Message,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

_call_types = {}


class VideoRule:
    def __init__(self, bot: Bot, user_id: int):
        self.bot = bot
        self.user_id = user_id

    def user_is_subscribed(self):
        if settings.DEBUG:
            logger.info('Skip check subscription')
            return True
        return self._check_subscribe(settings.MAIN_CHANNEL_ID)

    def need_subscribe(self, sender: Sender):
        buttons = [
            InlineKeyboardButton(settings.MAIN_CHANNEL_ID, url=settings.CHAT_INVITE_LINK),
            InlineKeyboardButton("Я сделяль!", callback_data="delete/"),
        ]
        sender.send(
            settings.MAIN_PHOTO,
            "Подпишитесь на основной канал для продолжения.",
            InlineKeyboardMarkup.from_column(buttons),
        )

    def _check_subscribe(self, channel: int) -> bool:
        """Проверка подписки на канал."""
        try:
            chat_member: ChatMember = self.bot.get_chat_member(
                f"@{channel}", self.user_id)
        except BadRequest:
            logger.warning(f"user {self.user_id} is not subscribed")
            return False

        status = chat_member.status
        if status in (ChatMember.RESTRICTED, ChatMember.LEFT, ChatMember.KICKED):
            logger.warning(f"user {self.user_id} has {status}")
            return False

        return True


class CallbackManager(ABC):

    def __init__(self, update: Update, context: CallbackContext, sender: Sender):
        self.update = update
        self.context = context
        self.sender = sender

    def send_reaction_on_callback(self, router: Router) -> Message:
        handler, args = router.get_handler(self.update.callback_query.data)
        query = self.update.callback_query.data
        _start = time()
        try:
            result = handler(self, *args)
            logger.info(f'handle {query} {handler.__name__}: {time() - _start}')
            return result
        finally:
            self.update.callback_query.answer()

    def publish_message(
            self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs
    ) -> None:
        return self.sender.publish(media, keyboard, **kwargs)
