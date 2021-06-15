import logging

from django.conf import settings

from netflix_bot import models
from netflix_bot.models import Movie
from netflix_bot.telegram_bot.manager import VideoManager
from netflix_bot.telegram_bot.uploader import Uploader

logger = logging.getLogger()


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


class MovieUploader(Uploader):
    uploader = settings.MOVIE_UPLOADER_ID
    manager = MovieManager
    model = Movie
