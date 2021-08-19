import logging
import traceback
import uuid
from functools import lru_cache
from random import shuffle
from time import time

from django.conf import settings
from telegram import Chat, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.error import TelegramError
from telegram.ext import (
    BaseFilter,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from .commands import Commands, movie, series, start
from .constants import MAIN_KEYBOARD, START_MESSAGE
from .managers.movie import MovieCallback
from .managers.series import SeriesCallback
from .messages import MovieUploadHandler, SeriesUploadHandler, callbacks
from .senders import InlineSender

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


class Channel(BaseFilter):
    """Фильтр по чат - это канал"""

    def filter(self, message):
        return message.chat.type in [Chat.CHANNEL]


def inline_query(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query

    if len(query) < 3:
        update.inline_query.answer([_get_inline_empty_answer()], cache_time=2000)
        return

    start = time()

    result = []
    movies = MovieCallback.search(query, MovieCallback.build_articles)
    series = SeriesCallback.search(query, SeriesCallback.build_articles)

    logger.info(f"Movie cache: {MovieCallback.search.cache_info()}")
    logger.info(f"Series cache: {SeriesCallback.search.cache_info()}")

    result.extend(movies)
    result.extend(series)

    if not result:
        update.inline_query.answer([_get_not_found_answer()], cache_time=2000)
        return

    shuffle(result)

    logger.info(f"Query: {query}, time: {time() - start}")

    update.inline_query.answer(result[:50], cache_time=300)


@lru_cache
def _get_inline_empty_answer() -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="Начните вводить название фильма",
        description="И я начну поиск)",
        photo_url=settings.MAIN_PHOTO,
        thumb_url=settings.MAIN_PHOTO,
        reply_markup=MAIN_KEYBOARD,
        input_message_content=InputTextMessageContent(START_MESSAGE),
    )


@lru_cache
def _get_not_found_answer() -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="К сожалению, по вашему запросу ничего не найдено...",
        photo_url=settings.MAIN_PHOTO,
        thumb_url=settings.MAIN_PHOTO,
        reply_markup=MAIN_KEYBOARD,
        input_message_content=InputTextMessageContent(START_MESSAGE),
    )


def search(update: Update, context: CallbackContext) -> None:
    """Поиск с клавиатуры."""
    query = update.effective_message.text
    sender = InlineSender(update, context)

    movies = MovieCallback(update, context, sender=sender)
    series = SeriesCallback(update, context, sender=sender)

    movies.founded(query, 1)
    series.founded(query, 1)


def up_bot() -> Dispatcher:
    if not settings.BOT_TOKEN:
        raise EnvironmentError("Empty bot token")

    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(Commands.START.value, start))
    dispatcher.add_handler(CommandHandler(Commands.MOVIE.value, movie))
    dispatcher.add_handler(CommandHandler(Commands.SERIES.value, series))

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

    # Common
    inline_handler = InlineQueryHandler(inline_query)
    callback_handler = CallbackQueryHandler(callbacks)
    # text_handler = MessageHandler(Filters.text, search)

    # Attach handlers
    dispatcher.add_handler(movie_upload_h, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_poster_handler, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_description_h, group=MOVIES_GROUP)

    dispatcher.add_handler(upload_series_h, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_poster_handler, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_description_h, group=SERIES_GROUP)

    dispatcher.add_handler(inline_handler)
    # dispatcher.add_handler(text_handler)

    dispatcher.add_handler(callback_handler)
    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
