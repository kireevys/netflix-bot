import logging
import traceback
from enum import Enum

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

from movies.handlers import handlers as movies_handlers
from series.handlers import handlers as series_handlers
from .commands import START_COMMAND, movie_link, search, start
from .messages import callbacks

logger = logging.getLogger(__name__)


class Groups(Enum):
    SERIES = 1
    MOVIES = 2


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
    for h in series_handlers:
        dispatcher.add_handler(h, group=Groups.SERIES.value)

    # Movies
    for h in movies_handlers:
        dispatcher.add_handler(h, group=Groups.MOVIES.value)

    # Callbacks
    dispatcher.add_handler(CallbackQueryHandler(callbacks))
    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
