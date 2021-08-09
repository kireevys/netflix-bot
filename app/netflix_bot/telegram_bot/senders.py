import logging
from abc import ABC, abstractmethod

from telegram import InlineKeyboardMarkup, InputMedia, InputMediaPhoto, Message, Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


class Sender(ABC):
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context

    @abstractmethod
    def send(
        self,
        photo: str,
        caption: str,
        keyboard: InlineKeyboardMarkup,
    ) -> None:
        ...

    def publish(
        self,
        media: InputMedia,
        keyboard: InlineKeyboardMarkup,
        **kwargs,
    ) -> None:
        ...

    def delete(self):
        self.context.bot.delete_message(
            message_id=self.update.effective_message.message_id,
            chat_id=self.update.effective_chat.id,
        )


class InlineSender(Sender):
    def send(
        self,
        photo: str,
        caption: str,
        keyboard: InlineKeyboardMarkup,
    ) -> None:
        return self.context.bot.send_photo(
            parse_mode="HTML",
            photo=photo,
            chat_id=self.update.effective_user.id,
            caption=caption,
            reply_markup=keyboard,
        )

    def publish(
        self,
        media: InputMediaPhoto,
        keyboard: InlineKeyboardMarkup,
        **kwargs,
    ) -> None:
        return self.context.bot.send_photo(
            parse_mode="HTML",
            photo=media.media,
            chat_id=self.update.effective_user.id,
            caption=media.caption,
            reply_markup=keyboard,
        )


class MessageSender(Sender):
    def send(
        self,
        photo: str,
        caption: str,
        keyboard: InlineKeyboardMarkup,
    ) -> None:
        return self.context.bot.send_photo(
            parse_mode="HTML",
            photo=photo,
            chat_id=self.update.effective_chat.id,
            caption=caption,
            reply_markup=keyboard,
        )

    def send_video(
        self,
        video,
        caption: str,
        keyboard: InlineKeyboardMarkup,
    ) -> Message:
        return self.context.bot.send_video(
            parse_mode="HTML",
            video=video,
            chat_id=self.update.effective_chat.id,
            caption=caption,
            reply_markup=keyboard,
        )

    def publish(
        self,
        media: InputMedia,
        keyboard: InlineKeyboardMarkup,
        **kwargs,
    ) -> None:
        """Публикацией сообщения считается замена существующего сообщения с Медиа.

        Так сделано, чтобы не морочить голову - что именно публикуется.
        """
        return self.context.bot.edit_message_media(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
            media=media,
            reply_markup=keyboard,
            **kwargs,
        )

    def replace(self, media: InputMedia, keyboard: InlineKeyboardMarkup, **kwargs):
        """Заменить сообщение можно только на сообщение с фоткой."""
        try:
            self.context.bot.delete_message(
                message_id=self.update.effective_message.id,
                chat_id=self.update.effective_chat.id,
            )
        except Exception as e:
            logger.info(e)

        media: InputMediaPhoto

        return self.context.bot.send(
            chat_id=self.update.effective_chat.id,
            photo=media.media,
            caption=media.caption,
            reply_markup=keyboard,
            **kwargs,
        )
