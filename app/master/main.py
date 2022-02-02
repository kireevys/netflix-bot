import logging
import traceback

from django.conf import settings
from master.handlers import MovieUploadHandler, SeriesUploadHandler
from telegram import TelegramError
from telegram.ext import Dispatcher, Filters, MessageHandler, Updater

logger = logging.getLogger(__name__)
error_logger = logging.getLogger("error")


def error_callback(update, context):
    try:
        raise context.error
    # except Unauthorized:
    #     # remove update.message.chat_id from conversation list
    # except BadRequest:
    #     # handle malformed requests - read more below!
    # except TimedOut:
    #     # handle slow connection problems
    # except NetworkError:
    #     # handle other connection problems
    # except ChatMigrated as e:
    #     # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        error_logger.error(traceback.format_exc())
    except Exception:
        error_logger.error(traceback.format_exc())


def run():
    if not settings.MASTER_TOKEN:
        raise EnvironmentError("Empty bot token")

    updater = Updater(token=settings.MASTER_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    # Uploaders
    # Series
    SERIES_GROUP = 1
    series_filter = (~Filters.command) & (Filters.chat(int(settings.UPLOADER_ID)))

    upload_series_h = MessageHandler(
        Filters.video & series_filter,
        SeriesUploadHandler.upload,
    )

    series_add_description_h = MessageHandler(
        Filters.text & series_filter, SeriesUploadHandler.add_description
    )
    series_add_poster_handler = MessageHandler(
        Filters.photo & series_filter, SeriesUploadHandler.add_poster
    )

    dispatcher.add_handler(upload_series_h, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_poster_handler, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_description_h, group=SERIES_GROUP)
    # Movies
    MOVIES_GROUP = 2
    movie_filter = (
        Filters.chat(chat_id=int(settings.MOVIE_UPLOADER_ID)) & ~Filters.command
    )
    movie_upload_h = MessageHandler(
        Filters.video & movie_filter,
        MovieUploadHandler.upload,
    )

    movie_add_description_h = MessageHandler(
        Filters.text & movie_filter, MovieUploadHandler.add_description
    )
    movie_add_poster_handler = MessageHandler(
        Filters.photo & movie_filter, MovieUploadHandler.add_poster
    )

    dispatcher.add_handler(movie_upload_h, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_poster_handler, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_description_h, group=MOVIES_GROUP)

    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
