import logging
import re

from django.conf import settings

from netflix_bot import models

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


class MovieManager(VideoManager):
    @classmethod
    def from_caption(cls, caption: str) -> "MovieManager":
        """
        Caption example:
            Неортодоксальная / Unorthodox
            1 Сезон / 4 Серия
            SUB
        """
        caption = cls._strip_ok_emoji(caption)

        title, *lang = caption.split("\n")

        title_ru, title_eng = [i.strip() for i in title.split("/")]

        lang = lang[0] if lang else models.Langs.RUS.name
        return cls(
            title_ru=title_ru,
            title_eng=title_eng,
            lang=lang,
        )

    def write(self, file_id, message_id):
        movie, _ = models.Movie.objects.get_or_create(
            title_ru=self.title_ru,
            title_eng=self.title_eng,
            lang=self.lang,
            file_id=file_id,
            message_id=message_id,
        )

        return movie

    def get_loader_format_caption(self):
        return f"{settings.EMOJI.get('ok')}{self.title}\n{self.lang}"

    def __str__(self):
        return f"{self.title} {self.lang}"