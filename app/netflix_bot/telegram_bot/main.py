import logging
import traceback

from django.conf import settings
from telegram import Chat
from telegram.error import TelegramError
from telegram.ext import (
    BaseFilter,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
)
from telegram.ext import Filters, MessageHandler
from telegram.ext import Updater

from .commands import START_COMMAND, movie_link, search, start
from .messages import MovieUploadHandler, SeriesUploadHandler, callbacks

logger = logging.getLogger(__name__)


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
        logger.error(traceback.format_exc())
    except Exception:
        logger.error(traceback.format_exc())


class Channel(BaseFilter):
    """Фильтр по чат - это канал"""

    def filter(self, message):
        return message.chat.type in [Chat.CHANNEL]


def up_bot() -> Dispatcher:
    if not settings.BOT_TOKEN:
        raise EnvironmentError("Empty bot token")

    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    # commands
    start_handler = CommandHandler(START_COMMAND, start)

    movie_search_handler = MessageHandler(
        Filters.text & ~Filters.command & ~Channel(), search
    )
    movie_link_handler = CommandHandler("movie", movie_link, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(movie_link_handler)

    dispatcher.add_handler(movie_search_handler)

    # Uploaders
    # Series
    SERIES_GROUP = 1
    series_filter = (~Filters.command) & (Filters.chat(int(settings.UPLOADER_ID)))

    upload_series_h = MessageHandler(
        Filters.video & series_filter,
        SeriesUploadHandler.upload,
    )

    series_add_description_h = MessageHandler(
        Filters.reply & series_filter, SeriesUploadHandler.add_description
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
        Filters.reply & movie_filter, MovieUploadHandler.add_description
    )
    movie_add_poster_handler = MessageHandler(
        Filters.photo & movie_filter, MovieUploadHandler.add_poster
    )

    dispatcher.add_handler(movie_upload_h, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_poster_handler, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_description_h, group=MOVIES_GROUP)

    # Callbacks
    dispatcher.add_handler(CallbackQueryHandler(callbacks))
    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
