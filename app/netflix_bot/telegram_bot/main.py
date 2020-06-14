import logging

from django.conf import settings
from telegram.error import TelegramError
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from .commands import start
from .messages import get_film_list, upload_video, callbacks

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
    except TelegramError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)


def up_bot() -> Dispatcher:
    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(
        Filters.text("Покажи сериалы") & (~Filters.command), get_film_list
    )
    upload_handler = MessageHandler(Filters.video & (~Filters.command), upload_video)

    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(upload_handler)
    dispatcher.add_handler(CallbackQueryHandler(callbacks))

    dispatcher.add_error_handler(error_callback)

    if not settings.DEBUG:
        logger.info('START POOLING')
        updater.start_polling(poll_interval=0.2)
    else:
        logger.info('START WEBHOOKS')

        url = f'https://{settings.SITE_DOMAIN}:{settings.BOT_PORT}/bot/{settings.BOT_TOKEN}'
        updater.start_webhook(listen='0.0.0.0',
                              port=settings.BOT_PORT,
                              url_path=f"bot/{settings.BOT_TOKEN}",
                              key=settings.KEY_PATH,
                              cert=settings.CERT_PATH,
                              webhook_url=url)

    return dispatcher
