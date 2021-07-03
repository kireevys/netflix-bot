import logging

from django.conf import settings
from django.db.models import Count
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from netflix_bot import models
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, callback
from netflix_bot.telegram_bot.user_interface.keyboards import (
    PaginationKeyboard,
    append_button,
)

logger = logging.getLogger(__name__)


class PathManager(CallbackManager):
    @callback("movie/$")
    def main(self, *_):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Список фильмов", callback_data="movie/all/"),
                    InlineKeyboardButton(
                        "Фильмы по жанрам", callback_data="movie/genre/"
                    ),
                ],
            ]
        )
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption="ФИЛЬМЫ"),
            keyboard=keyboard,
        )

    @callback("movie/all/$")
    @callback(r"movie/pagination\?p=(\d+)")
    def all(self, current: int = 1):
        current = int(current)
        movies = (
            models.Movie.objects.values("title_ru", "title_eng")
            .annotate(Count("lang"))
            .order_by("title_ru")
        )

        buttons = []
        for movie in movies:
            m: models.Movie = models.Movie.objects.filter(
                title_ru=movie.get("title_ru"), title_eng=movie.get("title_eng")
            ).first()
            buttons.append(
                InlineKeyboardButton(m.title, callback_data=f"movie/{m.id}?p={current}")
            )

        keyboard = PaginationKeyboard.from_pagination(
            buttons, page=current, path=f"movie/pagination?p="
        )
        keyboard = append_button(
            keyboard, [InlineKeyboardButton("Main", callback_data="movie/")]
        )

        return self.publish_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=f"Page {current}"),
            keyboard=keyboard,
        )

    @callback(r"movie/(\d+)\?p=(\d+)$")
    def movie(self, movie_id: int, page: int, *_):
        page = int(page)
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        buttons = [
            InlineKeyboardButton(
                m.lang, callback_data=f"movie/{m.id}?l={m.lang}&p={page}"
            )
            for m in langs
        ]
        buttons.append(
            InlineKeyboardButton("Back", callback_data=f"movie/pagination?p={page}")
        )

        keyboard = InlineKeyboardMarkup.from_column(buttons)
        return self.replace_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=movie.title),
            keyboard=keyboard,
        )

    @callback(r"movie/genre/$")
    def genres(self, *_):
        genres = (
            models.Genre.objects.all()
            .annotate(cnt_series=Count("movie"))
            .filter(cnt_series__gt=0)
        )

        buttons = [
            InlineKeyboardButton(
                genre.name, callback_data=f"movie/genre/{genre.id}?p=1"
            )
            for genre in genres.order_by("name")
        ]
        buttons.append(InlineKeyboardButton("Back", callback_data="movie/"))
        keyboard = InlineKeyboardMarkup.from_column(buttons)

        message_media = InputMediaPhoto(
            media=settings.MAIN_PHOTO, caption="Доступные жанры"
        )
        return self.publish_message(
            media=message_media,
            keyboard=keyboard,
        )

    @callback(r"movie/genre/(\d+)\?p=(\d+)")
    def concrete_genre(self, genre_id: int, page: int = 1):
        page = int(page)
        genre = models.Genre.objects.get(pk=genre_id)
        movies = models.Movie.objects.filter(genre=genre)

        keyboard = PaginationKeyboard.from_pagination(
            [
                InlineKeyboardButton(
                    movie.title,
                    callback_data=f"movie/genre/{genre.id}/{movie.id}?p={page}",
                )
                for movie in movies
            ],
            path=f"movie/genre/{genre_id}?p=",
            page=page,
        )

        append_button(
            keyboard, [InlineKeyboardButton("Back", callback_data="movie/genre/")]
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @callback(r"movie/genre/(\d+)/(\d+)\?p=(\d+)$")
    def genre_movie(self, genre_id: int, movie_id: int, page: str, *_):
        page = int(page)
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        buttons = [
            InlineKeyboardButton(
                m.lang, callback_data=f"movie/{m.id}?l={m.lang}&p={page}"
            )
            for m in langs
        ]
        buttons.append(
            InlineKeyboardButton(
                "Back", callback_data=f"movie/genre/{genre_id}?p={page}"
            )
        )

        keyboard = InlineKeyboardMarkup.from_column(buttons)
        return self.publish_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=movie.title),
            keyboard=keyboard,
        )

    @callback(r"movie/genre/(\d+)\?l=(\w+)&p=(\d+)$")
    def lang(self, movie_id: int, lang: str, page: int = 1, *_):
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        movie = langs.get(lang=lang)

        buttons = [
            InlineKeyboardButton(
                f"[ {l.lang} ]" if l.lang == lang else l.lang,
                callback_data=f"movie/{movie_id}?l={l.lang}&p={page}",
            )
            for l in langs
        ]
        buttons.append(
            InlineKeyboardButton(
                "Back", callback_data=f"movie/genre/{movie_id}?p={page}"
            )
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption=f"{movie.title}\n\n{movie.desc}"
            ),
            keyboard=InlineKeyboardMarkup.from_column(buttons),
        )

    @callback(r"movie/(\d+)\?l=(\w+)&p=(\d+)$")
    def lang(self, movie_id: int, lang: str, page: int = 1, *_):
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        movie = langs.get(lang=lang)

        buttons = [
            InlineKeyboardButton(
                f"[ {l.lang} ]" if l.lang == lang else l.lang,
                callback_data=f"movie/{movie_id}?l={l.lang}&p={page}",
            )
            for l in langs
        ]
        buttons.append(
            InlineKeyboardButton("Back", callback_data=f"movie/pagination?p={page}")
        )

        return self.replace_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption=f"{movie.title}\n\n{movie.desc}"
            ),
            keyboard=InlineKeyboardMarkup.from_column(buttons),
        )