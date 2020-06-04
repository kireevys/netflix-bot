import json
import logging

from django.db import IntegrityError
from django.db.models import Min
from telegram import InlineKeyboardButton
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers import SeriesManager, GridKeyboard
from .. import models

logger = logging.getLogger(__name__)


def callbacks(update: Update, context: CallbackContext):
    data = json.loads(update.callback_query.data)
    if data.get("type") == "series":
        series = models.Series.objects.get(pk=data.get("id"))
        seasons = (
            models.Episode.objects.filter(series=series)
            .values("season")
            .annotate(pk=Min("pk"))
        )
        buttons = []
        for nu, season in enumerate(seasons, start=1):
            title, pk = season.values()
            callback = json.dumps({"id": pk, "type": "episode"})
            button = InlineKeyboardButton(
                text=f"{title}", callback_data=callback
            )
            buttons.append([button])

        keyboard = GridKeyboard(buttons)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{series.title}",
            reply_markup=keyboard,
        )

        # context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)


def get_film_list(update: Update, context: CallbackContext):
    all_videos = models.Series.objects.all()

    buttons = []
    for nu, series in enumerate(all_videos, start=1):
        title, pk = series.title, series.pk
        callback = json.dumps({"id": pk, "type": "series"})
        button = InlineKeyboardButton(text=f"{nu:>3}: {title}", callback_data=callback)
        buttons.append(button)

    keyboard = InlineKeyboardMarkup.from_column(buttons)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что у меня есть",
        reply_markup=keyboard,
    )


def upload_video(update: Update, context: CallbackContext):
    logging.info(str(update))
    if update.channel_post.chat.username == "testkino01":

        manager = SeriesManager.parse_caption(caption=update.channel_post.caption)
        try:
            episode = manager.write(
                update.channel_post.video.file_id, update.effective_message.message_id
            )
        except IntegrityError:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Episode exists"
            )
            return

        logger.info(str(episode))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Added:\n{episode}"
        )
