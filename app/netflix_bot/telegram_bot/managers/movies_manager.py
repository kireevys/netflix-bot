import logging

from django.conf import settings
from django.db.models import Count
from telegram import Message, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo

from netflix_bot import models
from netflix_bot.models import Genre, Movie
from netflix_bot.telegram_bot.managers.series_manager import VideoManager
from netflix_bot.telegram_bot.user_interface.buttons import (
    ShowMoviesButton,
    MovieMainButton,
    MovieGenre,
    MovieGenres,
    MovieButton,
)
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, callback
from netflix_bot.telegram_bot.user_interface.keyboards import (
    get_movie_factory,
    PaginationKeyboardFactory,
)

logger = logging.getLogger(__name__)


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


class MoviesCallback(CallbackManager):
    main_callback_data = "movies_main"

    @callback("movies_main")
    def main_menu(self) -> Message:
        logger.info(f"{self.user} request movies list")

        keyboard = InlineKeyboardMarkup(
            [
                [ShowMoviesButton(1)],
                [MovieGenres()],
            ]
        )
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO),
            keyboard=keyboard,
        )

    @callback("movies_list")
    def publish_all_movies(self):
        factory = get_movie_factory()

        logger.info(f"{self.user} request film list")

        keyboard = factory.page_from_column(1)
        keyboard.inline_keyboard.append([MovieMainButton()])

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @callback("all_mv_genres")
    def publish_all_genres(self):
        genres = (
            Genre.objects.all()
            .annotate(cnt_series=Count("movie"))
            .filter(cnt_series__gt=0)
        )

        buttons = [MovieGenre(genre) for genre in genres.order_by("name")]
        keyboard = InlineKeyboardMarkup.from_column(buttons)
        keyboard.inline_keyboard.append([MovieMainButton()])

        message_media = InputMediaPhoto(
            media=settings.MAIN_PHOTO, caption="Доступные жанры"
        )
        return self.publish_message(
            media=message_media,
            keyboard=keyboard,
        )

    @callback("movies")
    def publish_movie(self) -> Message:
        movie = models.Movie.objects.get(pk=self.callback_data.get("id"))

        langs = models.Movie.objects.filter(title_ru=movie.title_ru)

        langs_button = []

        for movie_lang in langs:
            lang = movie_lang.lang
            lang = f"[ {lang} ]" if movie_lang == movie else lang

            langs_button.append(MovieButton(movie_lang, text=lang))

        keyboard = InlineKeyboardMarkup([langs_button, [ShowMoviesButton(1)]])

        return self.publish_message(
            media=InputMediaVideo(
                media=movie.file_id,
                caption=f"{movie.title} {movie.lang}\n\n{movie.desc or ''}",
            ),
            keyboard=keyboard,
        )

    @callback("genre_mv")
    def get_all_series_for_genre(self):
        genre = Genre.objects.get(pk=self.callback_data.get("id"))
        movies = Movie.objects.filter(genre=genre)

        keyboard = PaginationKeyboardFactory.from_queryset(
            movies, "movie"
        ).page_from_column(1)

        keyboard.inline_keyboard.append([MovieMainButton()])

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )
