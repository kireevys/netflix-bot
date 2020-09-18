import logging

from telegram import Update
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers.series_manager import SeriesCallback
from netflix_bot.telegram_bot.uploaders import SeriesUploader, MovieUploader
from ..models import Series, Movie

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    manager = SeriesCallback(update, context)
    manager.send_reaction_on_callback()


def add_description(update: Update, context: CallbackContext):
    uploader = SeriesUploader(update, context)
    try:
        series = uploader.add_description(update.effective_message.text)
        logger.info(f"update description for {series}")
    except Series.DoesNotExist:
        pass

    uploader = MovieUploader(update, context)
    try:
        series = uploader.add_description(update.effective_message.text)
        logger.info(f"update description for {series}")
    except Movie.DoesNotExist as e:
        raise e


def add_poster(update: Update, context: CallbackContext):
    logging.info(str(update))

    try:
        SeriesUploader(update, context).add_poster(
            update.channel_post.photo[-1].file_id
        )
    except (ConnectionAbortedError, ValueError):
        pass

    try:
        MovieUploader(update, context).add_poster(update.channel_post.photo[-1].file_id)
    except ConnectionAbortedError as e:
        logger.warning("This is not series or movie uploader")
        raise e


def upload_video(update: Update, context: CallbackContext):
    logging.info("Upload new video")

    try:
        SeriesUploader(update, context).upload()
    except (ConnectionAbortedError, ValueError):
        pass

    try:
        MovieUploader(update, context).upload()
    except ConnectionAbortedError as e:
        logger.warning("This is not series or movie uploader")
        raise e
