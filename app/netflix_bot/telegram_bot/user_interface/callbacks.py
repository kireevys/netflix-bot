import json
import logging
from abc import ABC

from django.conf import settings
from telegram import (
    Update,
    Bot,
    ChatMember,
    Message,
    InputMedia,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

_call_types = {}


def callback(name):
    def wrapper(fn):
        _call_types.update({name: fn})
        return fn

    return wrapper


class Callback:
    def __init__(self, callback_query: CallbackQuery):
        self._data = {}

        if callback_query:
            self._data = json.loads(callback_query.data)

        self.type = self._data.get("type")

    def get(self, item):
        return self._data.get(item)


class CallbackManager(ABC):
    main_callback_data = None

    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot: Bot = context.bot

        self.callback_data = Callback(self.update.callback_query)

        self.chat_id = self.update.effective_chat.id
        self.message_id = self.update.effective_message.message_id

        self.user = self.update.effective_user

    @classmethod
    def start_manager(cls, update: Update, context: CallbackContext):
        instance = cls(update, context)
        instance.callback_data.type = cls.main_callback_data

        instance.send_reaction_on_callback()

    def send_need_subscribe(self):
        invite_button = InlineKeyboardButton(
            "Подпишись!", url=settings.CHAT_INVITE_LINK
        )
        return self.bot.send_message(
            self.chat_id,
            "Просмотр недоступен без подписки на основной канал(((",
            reply_markup=InlineKeyboardMarkup([[invite_button]]),
        )

    def user_is_subscribed(self):
        if settings.DEBUG:
            return True

        try:
            chat_member: ChatMember = self.bot.get_chat_member(
                settings.MAIN_CHANNEL_ID, self.user.id
            )
        except BadRequest:
            logger.warning(f"user {self.user} is not subscribed")
            return False

        status = chat_member.status
        if status in ("restricted", "left", "kicked"):
            logger.warning(f"user {self.user} has {status}")
            return False

        return True

    def send_reaction_on_callback(self) -> Message:
        handler = _call_types.get(self.callback_data.type)
        return handler(self)

    def publish_message(
        self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs
    ) -> Message:
        return self.bot.edit_message_media(
            message_id=self.message_id,
            chat_id=self.chat_id,
            media=media,
            reply_markup=keyboard,
            **kwargs,
        )

    def it_my_message(self):
        return self.update.effective_message.from_user.name == self.bot.name

    def replace_message(
        self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs
    ) -> Message:
        if self.it_my_message():
            return self.publish_message(media=media, keyboard=keyboard)

        try:
            self.bot.delete_message(message_id=self.message_id, chat_id=self.chat_id)
        except Exception as e:
            logger.info(e)

        return self.bot.send_photo(
            chat_id=self.chat_id, photo=media.media, reply_markup=keyboard, **kwargs
        )
