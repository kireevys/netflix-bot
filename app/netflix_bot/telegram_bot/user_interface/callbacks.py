import logging
import re
from abc import ABC

from django.conf import settings
from telegram import (Bot, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, InputMedia, InputMediaPhoto, Message,
                      Update)
from telegram.error import BadRequest
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

_call_types = {}


def callback(regexp):
    def wrapper(fn):
        _call_types.update({regexp: fn})
        return fn

    return wrapper


def get_handler(route):
    for i in _call_types.keys():
        if re.findall(i, route):
            return _call_types[i], i
    else:
        logger.warning("Not found")


class CallbackManager(ABC):
    main_callback_data = None

    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot: Bot = context.bot

        self.callback_data = self.update.callback_query.data

        self.chat_id = self.update.effective_chat.id
        self.message_id = self.update.effective_message.message_id

        self.user = self.update.effective_user

    @classmethod
    def start_manager(cls, update: Update, context: CallbackContext):
        instance = cls(update, context)
        # instance.callback_data.type = cls.main_callback_data

        instance.send_reaction_on_callback()

    def send_need_subscribe(self):
        invite_button = InlineKeyboardButton("RUSFLIX", url=settings.CHAT_INVITE_LINK)
        return self.bot.send_message(
            self.chat_id,
            "Для просмотра подпишитесь на основной канал.",
            reply_markup=InlineKeyboardMarkup([[invite_button]]),
        )

    def user_is_subscribed(self):
        if settings.DEBUG:
            return True
        return all(map(self._check_subscribe, settings.MAIN_CHANNEL_ID))

    def _check_subscribe(self, channel: int) -> bool:
        """Проверка подписки на канал."""
        try:
            chat_member: ChatMember = self.bot.get_chat_member(channel, self.user.id)
        except BadRequest:
            logger.warning(f"user {self.user} is not subscribed")
            return False

        status = chat_member.status
        if status in ("restricted", "left", "kicked"):
            logger.warning(f"user {self.user} has {status}")
            return False

        return True

    def send_reaction_on_callback(self) -> Message:
        handler, regexp = get_handler(self.callback_data)
        args = re.search(regexp, self.update.callback_query.data).groups()
        try:
            return handler(self, *args)
        finally:
            self.update.callback_query.answer()

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

        media: InputMediaPhoto

        return self.bot.send_photo(
            chat_id=self.chat_id,
            photo=media.media,
            caption=media.caption,
            reply_markup=keyboard,
            **kwargs,
        )
