import logging
import re

from django.conf import settings
from django.db.models import Count, Q
from telegram import (InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, Message)

from netflix_bot import models
from netflix_bot.common import decodeb64
from netflix_bot.models import Genre, Series
from netflix_bot.my_lib import markdown
from netflix_bot.telegram_bot.user_interface.buttons import (AllGenresButton, BackButton, ChangeLanguage, EpisodeButton,
                                                             GenresButton, Language, MovieMainButton, NavigateButton,
                                                             SeasonButton, SeriesMainButton, ShowSeriesButton)
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, callback
from netflix_bot.telegram_bot.user_interface.keyboards import (GridKeyboard, PaginationKeyboardFactory, get_factory)

logger = logging.getLogger(__name__)


class VideoManager:
    def __init__(self, title_ru, title_eng, lang, **kwargs):
        self.title_ru = title_ru
        self.title_eng = title_eng
        self.lang = self.get_lang(lang.upper())

    @staticmethod
    def _strip_ok_emoji(caption: str) -> str:
        if caption.startswith(settings.EMOJI.get("ok")):
            caption = caption.strip(settings.EMOJI.get("ok"))

        return caption

    @property
    def title(self):
        return f"{self.title_ru} / {self.title_eng}"

    @staticmethod
    def get_lang(lang: str):
        if lang not in models.Langs:
            logger.info(f"incorrect lang {lang}. Using default")
            return models.Langs.RUS.name

        return lang


class SeriesManager(VideoManager):
    def __init__(self, title_ru, title_eng, lang, season, episode, **kwargs):
        super().__init__(title_ru, title_eng, lang, **kwargs)

        self.season = season
        self.episode = episode

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
    main_callback_data = "series_main"

    @callback("series_main")
    def main_menu(self) -> Message:
        logger.info(f"{self.user} request series list")

        keyboard = InlineKeyboardMarkup(
            [
                [ShowSeriesButton(1)],
                [AllGenresButton()],
                [MovieMainButton()],
            ]
        )
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption="СЕРИАЛЫ"),
            keyboard=keyboard,
        )

    @callback("se_search")
    def search(self):
        title: str = decodeb64(self.callback_data.get("search"))

        qs = models.Series.objects.filter(
            Q(title_eng__icontains=title) | Q(title_ru_upper__contains=title.upper())
        ).order_by("title_ru")
        caption = "Вот что я нашел" if qs else "Ничего не найдено. Главное меню"

        factory = get_factory(10, qs)

        logger.info("search series", extra=dict(user=self.user.__dict__))

        keyboard = factory.page_from_column(1)
        keyboard.inline_keyboard.append([SeriesMainButton()])

        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=caption),
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
        keyboard.inline_keyboard.append([SeriesMainButton()])

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @callback("lang")
    def publish_seasons_to_series(self) -> Message:
        series = models.Series.objects.get(pk=self.callback_data.get("id"))
        lang = self.callback_data.get("lang")

        lang_repr = models.Langs.repr(lang)

        buttons = [SeasonButton(season) for season in series.get_seasons(lang)]

        keyboard = GridKeyboard.from_column(buttons)
        keyboard.inline_keyboard.append([ChangeLanguage(series)])

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO,
                caption=f"{series.title} {lang_repr}\n\n{series.desc or ''}",
            ),
            keyboard=keyboard,
        )

    @callback("series")
    def publish_language(self) -> Message:
        """
        Возвращает Список доступных языков для сериала
        """
        series = models.Series.objects.get(pk=self.callback_data.get("id"))
        buttons = [Language(episode) for episode in series.get_languages()]

        keyboard = GridKeyboard.from_column(buttons)
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

        keyboard.inline_keyboard.append([BackButton(episodes.first())])

        caption = (
            f"Список серий {series.title} {models.Langs.repr(lang)}\n s{season_no}"
        )

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
        keyboard.inline_keyboard.append([SeriesMainButton()])

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

        keyboard.inline_keyboard.append([SeriesMainButton()])

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )
