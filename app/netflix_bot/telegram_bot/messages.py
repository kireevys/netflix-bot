import logging

from telegram import Update
from telegram.ext import CallbackContext

from movies.loader import MovieUploader

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from series.front.cb import SeriesCallback
from series.loader import SeriesUploader

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    manager = SeriesCallback(update, context)
    manager.send_reaction_on_callback()


class UploadHandler:
    uploader = None

    @classmethod
    def add_description(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).add_description(update.effective_message.text)

    @classmethod
    def add_poster(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).add_poster(update.channel_post.photo[-1].file_id)

    @classmethod
    def upload(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).upload()


class SeriesUploadHandler(UploadHandler):
    uploader = SeriesUploader


class MovieUploadHandler(UploadHandler):
    uploader = MovieUploader
