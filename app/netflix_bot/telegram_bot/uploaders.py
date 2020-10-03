import logging
from typing import Union

from django.conf import settings
from django.db import IntegrityError
from telegram import Update
from telegram.ext import CallbackContext

from netflix_bot.models import Series, Movie
from netflix_bot.telegram_bot.managers.movies_manager import MovieManager
from netflix_bot.telegram_bot.managers.series_manager import SeriesManager

logger = logging.getLogger(__name__)


class Uploader:
    uploader: int = None
    manager = None
    model: Union[Movie, Series] = None

    def __init__(self, update: Update, context: CallbackContext):
        self.bot = context.bot
        self.update = update

        if not self.is_upload_channel(self.update.channel_post.chat.id):
            logger.warning("Incorrect chat id for upload video")
            raise ConnectionAbortedError("Access denied")

    def get_models_for_add_poster(self, title_ru, title_eng):
        qs = self.model.objects.filter(title_ru=title_ru, title_eng=title_eng)
        if not qs:
            raise self.model.DoesNotExist()

        return qs

    def add_poster(self, file_id: str):
        manager = self.manager.from_caption(caption=self.update.channel_post.caption)
        models_qs = self.get_models_for_add_poster(
            title_ru=manager.title_ru, title_eng=manager.title_eng
        )

        models_qs.update(poster=file_id)

        self.bot.edit_message_caption(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
            caption=f"{settings.EMOJI.get('ok')} {self.update.channel_post.caption}",
        )
        logger.info(f"{models_qs} get new poster")

    def add_description(self, desc_text) -> model:
        models = self.model.get_by_message_id(
            self.update.effective_message.reply_to_message.message_id
        )

        models.update(desc=desc_text)

        logger.info(f"Edited description {models.first()}")

        self.bot.delete_message(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
        )

        return models.first()

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

        manager = self.manager.from_caption(caption=self.update.channel_post.caption)
        message = self.bot.send_video(
            chat_id=self.update.effective_chat.id,
            video=self.update.channel_post.video.file_id,
            caption=manager.get_loader_format_caption(),
        )

        try:
            video = manager.write(
                message.video.file_id,
                message.message_id,
            )
            logger.info(f"<{video}> successful loaded")
        except IntegrityError:
            logger.info(f"Loaded exists video <{manager}>. Message delete")
            self.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=message.message_id
            )
        finally:
            self.bot.delete_message(
                chat_id=self.update.effective_chat.id,
                message_id=self.update.effective_message.message_id,
            )

    @classmethod
    def is_upload_channel(cls, chat_id: int):
        return chat_id == int(cls.uploader)


class SeriesUploader(Uploader):
    uploader = settings.UPLOADER_ID
    manager = SeriesManager
    model = Series


class MovieUploader(Uploader):
    uploader = settings.MOVIE_UPLOADER_ID
    manager = MovieManager
    model = Movie
