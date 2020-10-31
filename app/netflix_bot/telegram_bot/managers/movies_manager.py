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
    NavigateButton,
    NavigateMovie,
    SeriesMainButton,
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
            [[ShowMoviesButton(1)], [MovieGenres()], [SeriesMainButton()]]
        )
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption="ФИЛЬМЫ"),
            keyboard=keyboard,
        )

    @callback('mv_search')
    def search(self):
        title_eng = self.callback_data.get("search")
        qs = (
            Movie.objects.filter(title_eng__icontains=title_eng)
            .values("title_ru", "title_eng")
            .annotate(Count("lang"))
            .order_by("title_ru")
        )

        caption = "Вот что я нашел" if qs else "Ничего не найдено. Главное меню"

        factory = get_movie_factory(per_page=10, qs=qs)

        logger.info(
            "search movies", extra=dict(user=self.user.__dict__, string=title_eng)
        )

        keyboard = factory.page_from_column(1, NavigateMovie)
        keyboard.inline_keyboard.append([MovieMainButton()])

        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=caption),
            keyboard=keyboard,
        )

    @callback("movies_list")
    def publish_all_movies(self):
        factory = get_movie_factory()

        logger.info(f"{self.user} request film list")

        keyboard = factory.page_from_column(1, NavigateMovie)
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
        if not self.user_is_subscribed():
            return self.send_need_subscribe()

        _before_watch_video = "Выберите озвучку"

        movie = models.Movie.objects.get(pk=self.callback_data.get("id"))

        movies_by_langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        movie_with_desc = movies_by_langs.filter(desc__isnull=False).first()

        desc = movie_with_desc.desc if movie_with_desc else str()

        langs_button = []

        if (
            movie.poster
            and self.update.effective_message.photo
            and _before_watch_video not in self.update.effective_message.caption
        ):
            media = InputMediaPhoto(
                media=movie.poster,
                caption=f"{movie.title}\n\n{desc}\n\n{_before_watch_video}",
            )
        else:
            media = InputMediaVideo(
                media=movie.file_id,
                caption=f"{movie.title}\n\n{desc}",
            )

        for movie_lang in movies_by_langs:
            lang = movie_lang.lang
            lang = (
                f"[ {lang} ]"
                if movie_lang == movie and isinstance(media, InputMediaVideo)
                else lang
            )

            langs_button.append(MovieButton(movie_lang, text=lang))

        keyboard = InlineKeyboardMarkup([langs_button, [ShowMoviesButton(1)]])

        return self.publish_message(
            media=media,
            keyboard=keyboard,
        )

    @callback("genre_mv")
    def get_all_series_for_genre(self):
        genre = Genre.objects.get(pk=self.callback_data.get("id"))
        movies = Movie.objects.filter(genre=genre)

        keyboard = PaginationKeyboardFactory.from_queryset(
            movies, "movie"
        ).page_from_column(1, NavigateMovie)

        keyboard.inline_keyboard.append([MovieMainButton()])

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @callback("nav_mv")
    def make_navigation(self):
        page = self.callback_data.get(NavigateButton.CURRENT)
        factory = get_movie_factory()

        keyboard = factory.page_from_column(page, NavigateMovie)
        keyboard.inline_keyboard.append([MovieMainButton()])

        message_media = InputMediaPhoto(
            media=settings.MAIN_PHOTO, caption=f"Страница {page}"
        )

        return self.publish_message(
            media=message_media,
            keyboard=keyboard,
        )
