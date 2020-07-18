import logging

from django.db import IntegrityError
from telegram import Update
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers import SeriesManager, CallbackManager

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    manager = CallbackManager(update, context)
    manager.send_reaction_on_callback()


def upload_video(update: Update, context: CallbackContext):
    logging.info(str(update))
    if update.channel_post.chat.username == "testkino01":

        manager = SeriesManager.parse_caption(caption=update.channel_post.caption)
        try:
            episode = manager.write(
                update.channel_post.video.file_id, update.effective_message.message_id
            )
        except IntegrityError:
            logger.info("Loaded exists episode %s", manager)
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Episode exists \n{manager}"
            )
            return

        logger.info(str(episode))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Added:\n{episode}"
        )
