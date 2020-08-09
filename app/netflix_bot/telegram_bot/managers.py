import json
import logging
import random
import re
import string
from abc import ABC

from django.conf import settings
from django.core.paginator import Paginator
from telegram import (
    Message,
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaVideo,
    InputMediaPhoto,
)
from telegram import Update
from telegram.bot import Bot
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from netflix_bot import models
from netflix_bot.telegram_bot.handlers import get_factory
from netflix_bot.telegram_bot.ui import (
    SeasonButton,
    EpisodeButton,
    GridKeyboard,
    FilmList,
    BackButton,
)

logger = logging.getLogger(__name__)


class SeriesManager(dict):
    def __init__(self, title, season, episode, lang):
        self.title = title
        self.season = season
        self.episode = episode
        self.lang = self.get_lang(lang.upper())
        super().__init__(title=title, season=season, episode=episode, lang=lang)

    @staticmethod
    def _strip_ok_emoji(caption: str) -> str:
        if caption.startswith(settings.EMOJI.get("ok")):
            caption = caption.strip(settings.EMOJI.get("ok"))

        return caption

    @classmethod
    def from_caption(cls, caption: str) -> "SeriesManager":
        """
        Caption example:
            Неортодоксальная / Unorthodox
            1 Сезон / 4 Серия
            SUB
        """
        caption = cls._strip_ok_emoji(caption)

        title, series, *lang = caption.split("\n")
        season, episode = re.findall(r"(\d+)", series)

        lang = lang[0] if lang else "empty"
        return cls(title=title, season=int(season), episode=int(episode), lang=lang)

    def _fake_write(self, file_id, message_id):
        series, _ = models.Series.objects.get_or_create(
            title=f"{self.title}_{random.choice(string.ascii_letters)}{random.randint(1, 9)}"
        )
        episode = models.Episode.objects.create(
            series=series,
            season=random.randint(1, 10),
            episode=random.randint(1, 10),
            lang=self.lang,
            file_id=file_id,
            message_id=message_id,
        )
        return episode

    @staticmethod
    def get_lang(lang: str):
        if lang not in models.Episode.Langs:
            logger.info(f"incorrect lang {lang}. Use default")
            return models.Episode.Langs.RUS.name

        return lang

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

    def get_loader_format_caption(self):
        return f"{settings.EMOJI.get('ok')}{self.title}\n{self.season} season / {self.episode} episode\n{self.lang}"

    def __str__(self):
        return f"{self.title} s{self.season}e{self.episode} {self.lang}"


_call_types = {}


def callback_type(fn):
    _call_types.update({fn.__name__: fn})


def send_need_subscribe(chat_id, bot: Bot):
    invite_button = InlineKeyboardButton("Подпишись!", url=settings.CHAT_INVITE_LINK)
    return bot.send_message(
        chat_id,
        "Просмотр недоступен без подписки на основной канал(((",
        reply_markup=InlineKeyboardMarkup([[invite_button]]),
    )


class CallbackManager(ABC):
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.callback_data = json.loads(update.callback_query.data)
        self.type = self.callback_data.get("type")
        self.context = context
        self.bot: Bot = context.bot
        self.chat_id = self.update.effective_chat.id

    def send_reaction_on_callback(self) -> Message:
        handler = _call_types.get(self.type)
        return handler(self)


class UIManager(CallbackManager):
    def _is_subscribed(self):
        try:
            chat_member: ChatMember = self.bot.get_chat_member(
                settings.MAIN_CHANNEL_ID, self.update.effective_user.id
            )
        except BadRequest:
            logger.warning(f"user {self.update.effective_user} is not subscribed")
            return True

        status = chat_member.status
        if status in ("restricted", "left", "kicked"):
            logger.warning(f"user {self.update.effective_user} has {status}")
            return False

        return True

    @callback_type
    def film_list(self):
        """
        Выбор сериала - возвращает сезоны
        :return:
        """
        factory = get_factory()

        logger.info(f"{self.update.effective_user} request film list")

        self.bot.edit_message_media(
            message_id=self.update.effective_message.message_id,
            chat_id=self.chat_id,
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            reply_markup=factory.page_from_column(1),
        )

    @callback_type
    def series(self) -> Message:
        """
        Возвращает Список серий в сезоне
        """
        series = models.Series.objects.get(pk=self.callback_data.get("id"))
        buttons = [SeasonButton(season) for season in series.get_seasons()]

        pagination_buttons = Paginator(buttons, settings.ELEMENTS_PER_PAGE)

        keyboard = GridKeyboard.from_grid(pagination_buttons.page(1))
        keyboard.inline_keyboard.append([FilmList(1)])

        return self.bot.edit_message_media(
            message_id=self.update.effective_message.message_id,
            chat_id=self.chat_id,
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO,
                caption=f"{series.title}\n\n{series.desc or ''}",
            ),
            reply_markup=keyboard,
        )

    @callback_type
    def season(self) -> Message:
        """
        Список сезонов
        """
        series, season_no, lang = (
            self.callback_data.get("series"),
            self.callback_data.get("id"),
            self.callback_data.get("lang"),
        )
        episodes = models.Episode.objects.filter(
            series=series, season=season_no, lang=lang
        ).order_by("episode")

        buttons = [EpisodeButton(episode) for episode in episodes]
        keyboard = GridKeyboard.from_grid(buttons)
        series = models.Series.objects.get(pk=series)

        keyboard.inline_keyboard.append([BackButton(series)])

        caption = f"Список серий {series.title}\n s{season_no}"

        logger.info(f"{self.update.effective_user} GET {caption}")

        return self.context.bot.edit_message_media(
            message_id=self.update.effective_message.message_id,
            chat_id=self.chat_id,
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO, caption=caption
            ),
            reply_markup=keyboard,
        )

    @callback_type
    def episode(self) -> Message:
        if not self._is_subscribed():
            return send_need_subscribe(self.chat_id, self.bot)

        episode = models.Episode.objects.get(id=self.callback_data.get("id"))
        caption = f"{episode.series.title} s{episode.season}e{episode.episode}"

        buttons = [
            EpisodeButton(episode)
            for episode in (episode.get_previous(), episode.get_next())
            if episode is not None
        ]

        keyboard = InlineKeyboardMarkup.from_row(buttons)
        keyboard.inline_keyboard.append([SeasonButton(episode.get_season())])

        logger.info(f"{self.update.effective_user} GET {caption}")

        return self.bot.edit_message_media(
            message_id=self.update.effective_message.message_id,
            chat_id=self.chat_id,
            media=InputMediaVideo(episode.file_id, caption=caption),
            reply_markup=keyboard,
        )

    @callback_type
    def navigate(self):
        page = self.callback_data.get("current")
        factory = get_factory()

        keyboard = factory.page_from_column(page)

        return self.bot.edit_message_media(
            message_id=self.update.effective_message.message_id,
            chat_id=self.chat_id,
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption=f"Страница {page}"
            ),
            reply_markup=keyboard,
        )
