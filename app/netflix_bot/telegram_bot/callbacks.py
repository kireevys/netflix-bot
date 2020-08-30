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
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

_call_types = {}


def callback(name):
    def wrapper(fn):
        _call_types.update({name: fn})

    return wrapper


class CallbackManager(ABC):
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot: Bot = context.bot

        self.callback_data = json.loads(update.callback_query.data)
        self.type = self.callback_data.get("type")

        self.chat_id = self.update.effective_chat.id
        self.message_id = self.update.effective_message.message_id

        self.user = self.update.effective_user

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
        try:
            chat_member: ChatMember = self.bot.get_chat_member(
                settings.MAIN_CHANNEL_ID, self.user.id
            )
        except BadRequest:
            logger.warning(f"user {self.user} is not subscribed")
            return False  # TODO: Залепа для бота без админки

        status = chat_member.status
        if status in ("restricted", "left", "kicked"):
            logger.warning(f"user {self.user} has {status}")
            return False

        return True

    def send_reaction_on_callback(self) -> Message:
        handler = _call_types.get(self.type)
        return handler(self)

    def publish_message(
        self, media: InputMedia, keyboard: InlineKeyboardMarkup
    ) -> Message:
        return self.bot.edit_message_media(
            message_id=self.message_id,
            chat_id=self.chat_id,
            media=media,
            reply_markup=keyboard,
        )
