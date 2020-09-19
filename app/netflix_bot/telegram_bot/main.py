import logging
import traceback

from django.conf import settings
from telegram.error import TelegramError
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from .commands import start, SERIES_START, START_COMMAND, MOVIES_START

# from .handlers import starting_series
from .managers.movies_manager import MoviesCallback
from .managers.series_manager import SeriesCallback
from .messages import upload_video, callbacks, add_description, add_poster

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


def up_bot() -> Dispatcher:
    if not settings.BOT_TOKEN:
        raise EnvironmentError("Empty bot token")

    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    start_handler = CommandHandler(START_COMMAND, start)
    dispatcher.add_handler(start_handler)

    watch_series_handler = MessageHandler(
        Filters.text(SERIES_START) & (~Filters.command),
        SeriesCallback.start_manager,
    )

    watch_movie_handler = MessageHandler(
        Filters.text(MOVIES_START) & (~Filters.command),
        MoviesCallback.start_manager,
    )

    upload_series_handler = MessageHandler(
        Filters.video & (~Filters.command) & (~Filters.update.edited_channel_post),
        upload_video,
    )
    edit_description_handler = MessageHandler(
        Filters.reply & (~Filters.command), add_description
    )
    add_poster_handler = MessageHandler(Filters.photo & (~Filters.command), add_poster)

    dispatcher.add_handler(watch_series_handler)
    dispatcher.add_handler(watch_movie_handler)

    dispatcher.add_handler(upload_series_handler)
    dispatcher.add_handler(add_poster_handler)

    dispatcher.add_handler(edit_description_handler)
    dispatcher.add_handler(CallbackQueryHandler(callbacks))

    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
