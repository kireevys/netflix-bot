import logging

from django.conf import settings
from django.db import IntegrityError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from netflix_bot.models import Series
from netflix_bot.telegram_bot.managers import SeriesManager

logger = logging.getLogger(__name__)


class VideoUploader:
    def __init__(self, update: Update, context: CallbackContext):
        self.bot = context.bot
        self.update = update
        if not self.is_upload_channel(self.update.channel_post.chat.id):
            logger.warning("Incorrect chat id for upload video")
            raise ConnectionAbortedError("Access denied")

    @staticmethod
    def is_upload_channel(chat_id: int):
        return chat_id == int(settings.UPLOADER_ID)

    def get_description_keyboard(self):
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Добавить описание", callback_data="Test", force_reply=True
                    )
                ]
            ]
        )

    def add_poster(self, file_id: str):
        manager = SeriesManager.from_caption(caption=self.update.channel_post.caption)
        series = Series.objects.get(title_ru=manager.title_ru)
        series.poster = file_id
        series.save()

        self.bot.edit_message_caption(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
            caption=f"{settings.EMOJI.get('ok')} {self.update.channel_post.caption}",
        )
        logger.info(f"{series} get new poster")

        return series

    def add_description(self, desc_text) -> Series:
        series = Series.objects.get(
            episode__message_id=self.update.effective_message.reply_to_message.message_id
        )
        series.desc = desc_text
        series.save()

        self.bot.delete_message(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
        )

        return series

    def upload(self):
        """
        Механика
            1. Парсим описание пришедшего сообщения
            2. Отправляем сообщение с видосом ботом
            3. Пытаемся сохранить
                Если уже эпизод уже существует - удаляем сообщение от бота
            4. Удаляем исходное сообщение

        Это надо для того, чтобы хранилище оставалось чистым независимо от того,
        откуда месседж - пересланный или загруженный админом.

        В любом случае - его можно будет модифицировать.
        """
        logger.info(str(self.update))

        manager = SeriesManager.from_caption(caption=self.update.channel_post.caption)
        message = self.bot.send_video(
            chat_id=self.update.effective_chat.id,
            video=self.update.channel_post.video.file_id,
            caption=manager.get_loader_format_caption(),
        )

        try:
            episode = manager.write(message.video.file_id, message.message_id,)
            logger.info(f"<{episode}> successful loaded")
        except IntegrityError:
            logger.info(f"Loaded exists episode <{manager}>. Message delete")
            self.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=message.message_id
            )
        finally:
            self.bot.delete_message(
                chat_id=self.update.effective_chat.id,
                message_id=self.update.effective_message.message_id,
            )
