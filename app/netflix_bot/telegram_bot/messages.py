import logging

from django.db import IntegrityError
from telegram import Update
from telegram.ext import CallbackContext

from netflix_bot import models

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers import SeriesManager, CallbackManager
from .ui import SeriesButton, PaginationKeyboard

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


def get_film_list(update: Update, context: CallbackContext):
    all_videos = models.Series.objects.all()

    buttons = [SeriesButton(series) for series in all_videos]
    keyboard = PaginationKeyboard.from_column(buttons)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что у меня есть",
        reply_markup=keyboard,
    )
