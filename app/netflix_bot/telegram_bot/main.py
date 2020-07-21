import logging
import traceback

from django.conf import settings
from telegram.error import TelegramError
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from .commands import start
from .handlers import get_film_list
from .messages import upload_video, callbacks

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

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    watch_handler = MessageHandler(
        Filters.text("Покажи сериалы") & (~Filters.command), get_film_list,
    )

    upload_handler = MessageHandler(Filters.video & (~Filters.command), upload_video)

    dispatcher.add_handler(watch_handler)
    dispatcher.add_handler(upload_handler)
    dispatcher.add_handler(CallbackQueryHandler(callbacks))

    dispatcher.add_error_handler(error_callback)

    logger.info("START POOLING")
    updater.start_polling(poll_interval=0.2)

    return dispatcher
