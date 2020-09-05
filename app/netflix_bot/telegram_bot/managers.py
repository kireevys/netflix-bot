import logging
import random
import re
import string

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from telegram import (
    Message,
    InlineKeyboardMarkup,
    InputMediaVideo,
    InputMediaPhoto,
)

from netflix_bot import models
from netflix_bot.models import Genre, Series
from netflix_bot.telegram_bot.user_interface.buttons import (
    BackButton,
    SeasonButton,
    ShowSeriesButton,
    EpisodeButton,
    AllGenresButton,
    SeriesMainButton,
    GenresButton,
    NavigateButton,
)
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, callback
from netflix_bot.telegram_bot.user_interface.keyboards import (
    GridKeyboard,
    get_factory,
    PaginationKeyboardFactory,
)
from ..my_lib import markdown

logger = logging.getLogger(__name__)


class SeriesManager:
    def __init__(self, title_ru, title_eng, season, episode, lang):
        self.title_ru = title_ru
        self.title_eng = title_eng
        self.season = season
        self.episode = episode
        self.lang = self.get_lang(lang.upper())

    @property
    def title(self):
        return f"{self.title_ru} / {self.title_eng}"

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

        title_ru, title_eng = [i.strip() for i in title.split("/")]

        lang = lang[0] if lang else "empty"
        return cls(
            title_ru=title_ru,
            title_eng=title_eng,
            season=int(season),
            episode=int(episode),
            lang=lang,
        )

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
            logger.info(f"incorrect lang {lang}. Using default")
            return models.Episode.Langs.RUS.name

        return lang

    def write(self, file_id, message_id):
        series, _ = models.Series.objects.get_or_create(
            title_ru=self.title_ru, title_eng=self.title_eng
        )
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


class SeriesCallback(CallbackManager):
    @callback("series_main")
    def main_menu(self) -> Message:
        logger.info(f"{self.user} request series list")

        keyboard = InlineKeyboardMarkup(
            [
                [ShowSeriesButton(1)],
                [AllGenresButton()],
            ]
        )
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO),
            keyboard=keyboard,
        )

    @callback("series_list")
    def publish_all_series(self):
        """
        Выбор сериала - возвращает сезоны
        """
        factory = get_factory()

        logger.info(f"{self.user} request film list")

        keyboard = factory.page_from_column(1)

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @callback("series")
    def publish_seasons_to_series(self) -> Message:
        """
        Возвращает Список серий в сезоне
        """
        series = models.Series.objects.get(pk=self.callback_data.get("id"))
        buttons = [SeasonButton(season) for season in series.get_seasons()]

        pagination_buttons = Paginator(buttons, settings.ELEMENTS_PER_PAGE)

        keyboard = GridKeyboard.from_grid(pagination_buttons.page(1))
        keyboard.inline_keyboard.append([ShowSeriesButton(1)])

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO,
                caption=f"{series.title}\n\n{series.desc or ''}",
            ),
            keyboard=keyboard,
        )

    @callback("season")
    def publish_all_episodes_for_season(self) -> Message:
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

        logger.info(f"{self.user} GET {caption}")

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO, caption=caption
            ),
            keyboard=keyboard,
        )

    @callback("episode")
    def publish_episode(self) -> Message:
        if not self.user_is_subscribed():
            return self.send_need_subscribe()

        episode = models.Episode.objects.get(id=self.callback_data.get("id"))

        episode_index = f"*__s{episode.season}e{episode.episode}__*"
        series_title = markdown.escape(episode.series.title)
        caption = f"{series_title}\n\n" f"{episode_index}"

        buttons = [
            EpisodeButton(episode, text=side)
            for episode, side in (episode.get_previous(), episode.get_next())
            if episode is not None
        ]

        keyboard = InlineKeyboardMarkup.from_row(buttons)
        keyboard.inline_keyboard.append([SeasonButton(episode.get_season())])

        logger.info(f"{self.update.effective_user} GET {caption}")

        return self.publish_message(
            media=InputMediaVideo(
                episode.file_id, caption=caption, parse_mode="MarkdownV2"
            ),
            keyboard=keyboard,
        )

    @callback("all_genres")
    def publish_all_genres(self):
        genres = (
            Genre.objects.all()
            .annotate(cnt_series=Count("series"))
            .filter(cnt_series__gt=0)
        )

        buttons = [GenresButton(genre) for genre in genres.order_by("name")]
        keyboard = InlineKeyboardMarkup.from_column(buttons)
        keyboard.inline_keyboard.append([SeriesMainButton()])

        message_media = InputMediaPhoto(
            media=settings.MAIN_PHOTO, caption="Доступные жанры"
        )
        return self.publish_message(
            media=message_media,
            keyboard=keyboard,
        )

    @callback("navigate")
    def make_navigation(self):
        page = self.callback_data.get(NavigateButton.CURRENT)
        factory = get_factory()

        keyboard = factory.page_from_column(page)

        message_media = InputMediaPhoto(
            media=settings.MAIN_PHOTO, caption=f"Страница {page}"
        )

        return self.publish_message(
            media=message_media,
            keyboard=keyboard,
        )

    @callback("genre")
    def get_all_series_for_genre(self):
        genre = Genre.objects.get(pk=self.callback_data.get("id"))
        series = Series.objects.filter(genre=genre)

        keyboard = PaginationKeyboardFactory.from_queryset(
            series, "series"
        ).page_from_column(1)

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )
