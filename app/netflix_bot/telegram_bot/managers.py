import json
import re

from telegram import Message
from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

from netflix_bot import models
from netflix_bot.telegram_bot.ui import GridKeyboard


class SeriesManager(dict):
    @classmethod
    def parse_caption(cls, caption) -> "SeriesManager":
        """
        Caption example:
            Неортодоксальная / Unorthodox
            1 Сезон / 4 Серия
            SUB
        """
        title, series, *lang = caption.split("\n")
        season, episode = re.findall(r"(\d+)", series)

        lang = lang[0].upper() if lang else models.Episode.Langs.RUS
        return cls(title=title, season=season, episode=episode, lang=lang)

    def __init__(self, title, season, episode, lang):
        self.title = title
        self.season = season
        self.episode = episode
        self.lang = lang
        super().__init__(title=title, season=season, episode=episode, lang=lang)

    def write(self, file_id, message_id):
        series, _ = models.Series.objects.get_or_create(title=self.title)
        episode = models.Episode.objects.create(
            series=series,
            season=self.season,
            episode=self.episode,
            lang=self.lang,
            file_id=file_id,
            message_id=message_id,
        )
        return episode

    def __str__(self):
        return f"{self.title} s{self.season}e{self.episode}"


_call_types = {}


def callback_type(fn):
    _call_types.update({fn.__name__: fn})


class CallbackManager:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.callback_data = json.loads(update.callback_query.data)
        self.type = self.callback_data.get("type")
        self.context = context
        self.bot = context.bot
        self.handler = _call_types.get(self.type)
        self.chat_id = self.update.effective_chat.id

    @callback_type
    def series(self) -> Message:
        series = models.Series.objects.get(pk=self.callback_data.get("id"))
        keyboard = get_seasons_list(series)

        return self.context.bot.send_message(
            chat_id=self.chat_id, text=f"Сезоны {series.title}", reply_markup=keyboard,
        )

    @callback_type
    def season(self) -> Message:
        series, season_no, lang = (
            self.callback_data.get("series"),
            self.callback_data.get("no"),
            self.callback_data.get("lang"),
        )
        keyboard = get_episode_list(series, season_no, lang)
        series = models.Series.objects.get(pk=series)
        return self.context.bot.send_message(
            chat_id=self.chat_id,
            text=f"Список серий {series.title}\n s{season_no}",
            reply_markup=keyboard,
        )

    @callback_type
    def episode(self) -> Message:
        file_id = models.Episode.objects.get(id=self.callback_data.get("id")).file_id
        return self.bot.send_video(chat_id=self.chat_id, video=file_id)

    def send_reaction_on_callback(self) -> Message:
        return self.handler(self)


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
