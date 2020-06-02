import logging
import re

from telegram import Update
from telegram.ext import CallbackContext

from .. import models

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


def get_video(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="DONE")


def echo(update: Update, context: CallbackContext):
    all_videos = models.Series.objects.all()
    s = '\n'.join([f"{nu:<5}. {i.video.title}" for nu, i in enumerate(all_videos, start=1)])
    context.bot.send_message(chat_id=update.effective_chat.id, text=s)


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
