import logging

from django.conf import settings
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from .commands import start
from .messages import echo, upload_video

logger = logging.getLogger(__name__)


def up_bot():
    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text("film") & (~Filters.command), echo)
    upload_handler = MessageHandler(Filters.video & (~Filters.command), upload_video)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(upload_handler)

    updater.start_polling(poll_interval=0.2)
