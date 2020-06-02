import logging
import re

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .. import models
import json

logger = logging.getLogger(__name__)
video_type = models.Video.VideoType


def parser(caption: str) -> dict:
    """
    Caption example:
        Неортодоксальная / Unorthodox
        1 Сезон / 4 Серия
        SUB
    :param caption:
    :return:
    """
    title, series, lang = caption.split("\n")
    season, episode = re.findall(r"(\d+)", series)

    return {"title": title, "season": season, "episode": episode, "lang": lang}


def button(update: Update, context: CallbackContext):
    data = json.loads(update.callback_query.data)
    file_id = models.Series.objects.get(pk=data.get("id")).file_id

    context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)


def get_film_list(update: Update, context: CallbackContext):
    all_videos = models.Series.objects.all()

    buttons = []
    for nu, series in enumerate(all_videos, start=1):
        callback = json.dumps({"id": series.pk})
        button = InlineKeyboardButton(
            text=f"{nu:>3}: {series.video.title}", callback_data=callback
        )
        buttons.append(button)

    keyboard = InlineKeyboardMarkup([buttons])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что у меня есть",
        reply_markup=keyboard,
    )


def upload_video(update: Update, context: CallbackContext):
    logging.info(str(update))
    if update.effective_chat.id == -1001392439062:
        attrs = parser(caption=update.channel_post.caption)
        video = models.Video.add(
            file_id=update.channel_post.video.file_id,
            message_id=update.effective_message.message_id,
            **attrs,
        )

        logger.info(str(video))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Added:\n{video}"
        )
