import logging
from abc import ABC

from django.conf import settings
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

from netflix_bot.telegram_bot.senders import Sender

logger = logging.getLogger(__name__)

_call_types = {}


class VideoRule:
    def __init__(self, bot: Bot, user_id: int):
        self.bot = bot
        self.user_id = user_id

    def user_is_subscribed(self):
        if settings.DEBUG:
            return True
        return all(map(self._check_subscribe, settings.MAIN_CHANNEL_ID))

    def need_subscribe(self, sender: Sender):
        buttons = [
            InlineKeyboardButton("RUSFLIX_BOT", url=settings.CHAT_INVITE_LINK),
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
            chat_member: ChatMember = self.bot.get_chat_member(channel, self.user_id)
        except BadRequest:
            logger.warning(f"user {self.user_id} is not subscribed")
            return False

        status = chat_member.status
        if status in ("restricted", "left", "kicked"):
            logger.warning(f"user {self.user_id} has {status}")
            return False

        return True


class CallbackManager(ABC):
    main_callback_data = None

    def __init__(self, update: Update, context: CallbackContext, sender: Sender):
        self.update = update
        self.context = context
        self.sender = sender

    def send_reaction_on_callback(self, router) -> Message:
        handler, args = router.get_handler(self.update.callback_query.data)
        try:
            return handler(self, *args)
        finally:
            self.update.callback_query.answer()

    def publish_message(
        self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs
    ) -> None:
        return self.sender.publish(media, keyboard, **kwargs)

    def replace_message(
        self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs
    ) -> None:
        return self.sender.replace(media, keyboard, **kwargs)
