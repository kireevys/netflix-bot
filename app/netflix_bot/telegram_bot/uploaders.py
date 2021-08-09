import logging
from abc import ABC
from typing import Any, Union

from django.conf import settings
from django.db import IntegrityError
from netflix_bot.models import Movie, Series
from netflix_bot.telegram_bot.managers.managers import MovieManager, SeriesManager
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger("uploader")


class Uploader(ABC):
    uploader: int = None
    manager = None
    model: Union[Movie, Series] = None

    def __init__(self, update: Update, context: CallbackContext):
        self.bot = context.bot
        self.update = update

        if not self.is_upload_channel(self.update.channel_post.chat.id):
            logger.warning("Incorrect chat id for upload video")
            raise ConnectionAbortedError("Access denied")

    def after_upload(self, video: Any):
        ...

    def after_description(self, desc_text: str):
        ...

    def after_poster(self, file_id: str):
        ...

    def get_models_for_add_poster(self, title_ru, title_eng):
        qs = self.model.objects.filter(title_ru=title_ru, title_eng=title_eng)
        if not qs:
            raise self.model.DoesNotExist()

        return qs

    def add_poster(self, file_id: str):
        title = self.manager._strip_ok_emoji(self.update.channel_post.caption)
        ru, en = [i.strip() for i in title.split("/")]
        models_qs = self.get_models_for_add_poster(title_ru=ru, title_eng=en)

        models_qs.update(poster=file_id)

        self.bot.edit_message_caption(
            chat_id=self.update.effective_chat.id,
            message_id=self.update.effective_message.message_id,
            caption=f"{settings.EMOJI.get('ok')} {title}",
        )
        logger.info(f"{models_qs} get new poster")
        self.after_poster(file_id)

    def add_description(self, desc_text) -> model:
        try:
            title, body = desc_text.split("|")
            ru, en = title.split("/")
            models = self.model.objects.filter(
                title_ru=ru.strip(), title_eng=en.strip()
            )
            if not models:
                logger.warning("Cant find %s for description", title)
                raise ValueError

            models.update(desc=body.strip())

            logger.info(f"Edited description {models.first()}")
            self.after_description(desc_text)
        finally:
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
            self.after_upload(video)
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
