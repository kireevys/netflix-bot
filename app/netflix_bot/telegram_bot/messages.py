import logging

from netflix_bot.telegram_bot.uploaders import MovieUploader, SeriesUploader
from telegram import Update
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers.movie import MovieCallback
from .managers.series import SeriesCallback
from .senders import InlineSender, MessageSender
from .user_interface.router import router

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    if update.effective_chat:
        sender = MessageSender(update, context)
    else:
        sender = InlineSender(update, context)

    handler, args = router.get_handler(update.callback_query.data)

    module = handler.__module__.split(".")[-1]

    if module == "movie":
        manager = MovieCallback(update, context, sender)
    elif module == "series":
        manager = SeriesCallback(update, context, sender)
    else:
        raise ValueError

    manager.send_reaction_on_callback(handler, args)


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
