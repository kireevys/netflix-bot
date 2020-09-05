import logging

from telegram import Update
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers import SeriesCallback
from .uploader import VideoUploader

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    manager = SeriesCallback(update, context)
    manager.send_reaction_on_callback()


def add_description(update: Update, context: CallbackContext):
    uploader = VideoUploader(update, context)
    series = uploader.add_description(update.effective_message.text)
    logger.info(f"update description for {series}")


def add_poster(update: Update, context: CallbackContext):
    logging.info(str(update))
    VideoUploader(update, context).add_poster(update.channel_post.photo[-1].file_id)


def upload_video(update: Update, context: CallbackContext):
    logging.info(str(update))
    VideoUploader(update, context).upload()
