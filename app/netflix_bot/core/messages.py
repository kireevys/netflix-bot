import json
import logging

from django.db import IntegrityError
from telegram import InlineKeyboardButton
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example
from .managers import SeriesManager, GridKeyboard
from .. import models

logger = logging.getLogger(__name__)


def get_seasons_list(series: models.Series):
    seasons = series.get_seasons()

    buttons = []
    for nu, season in enumerate(seasons, start=1):
        season_no = season.get("season")
        lang = season.get("lang")
        callback = json.dumps(
            {"no": season_no, "series": series.pk, "lang": lang, "type": "season"}
        )
        button = InlineKeyboardButton(
            text=f"{season_no:<3} {lang}", callback_data=callback
        )
        buttons.append([button])

    keyboard = GridKeyboard(buttons)
    return keyboard


def get_episode_list(series: models.Series, season: int, lang: str) -> GridKeyboard:
    episodes = models.Episode.objects.filter(
        series=series, season=season, lang=lang
    ).order_by("episode")

    buttons = []
    for nu, episode in enumerate(episodes, start=1):
        callback = json.dumps({"id": episode.id, "type": "episode"})
        button = InlineKeyboardButton(
            text=f"{episode.episode:<3} {lang}", callback_data=callback
        )
        buttons.append([button])

    keyboard = GridKeyboard(buttons)
    return keyboard


def callbacks(update: Update, context: CallbackContext):
    data = json.loads(update.callback_query.data)
    if data.get("type") == "series":
        series = models.Series.objects.get(pk=data.get("id"))
        keyboard = get_seasons_list(series)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Сезоны {series.title}",
            reply_markup=keyboard,
        )
    elif data.get("type") == "season":
        series, season_no, lang = data.get("series"), data.get("no"), data.get("lang")
        keyboard = get_episode_list(series, season_no, lang)
        series = models.Series.objects.get(pk=series)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Список серий {series.title}\n s{season_no}",
            reply_markup=keyboard,
        )
    elif data.get("type") == "episode":
        file_id = models.Episode.objects.get(id=data.get("id")).file_id

        context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)


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
                chat_id=update.effective_chat.id, text="Episode exists"
            )
            return

        logger.info(str(episode))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Added:\n{episode}"
        )
