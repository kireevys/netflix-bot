import functools
import logging
import uuid
from typing import List

from django.conf import settings
from django.db.models import Count, Q
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputMediaPhoto,
    InputMediaVideo,
    InputTextMessageContent,
)

from netflix_bot import models
from netflix_bot.models import Movie
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, VideoRule
from netflix_bot.telegram_bot.user_interface.keyboards import (
    PaginationKeyboard,
    append_button,
)
from netflix_bot.telegram_bot.user_interface.router import Route, router

logger = logging.getLogger(__name__)


class MovieCallback(CallbackManager):
    @router.add_method("^/$")
    def root(self):
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Все фильмы", callback_data="movie/")],
                [InlineKeyboardButton("Все сериалы", callback_data="series/")],
            ]
        )

        about_search = (
            "Смотри весь список фильмов и сериалов, "
            "используя кнопки ниже или воспользуйся поиском,"
            f"напиши {self.context.bot.get_me().name} и начни искать."
        )

        self.sender.publish(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=about_search),
            keyboard=keyboard,
        )

    @router.add_method("movie/$")
    def main(self, *_):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Список фильмов", callback_data="movie/all/"),
                ],
                [InlineKeyboardButton("Главная", callback_data="/"), ]
            ]
        )
        return self.publish_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption="ФИЛЬМЫ"),
            keyboard=keyboard,
        )

    @router.add_method("movie/all/$")
    @router.add_method(r"movie/pagination\?p=(\d+)")
    def all(self, current: int = 1):
        current = int(current)
        movies = models.Movie.objects.values("title_ru", "title_eng").annotate(Count("lang")).order_by("title_ru")

        buttons = []
        for movie in movies:
            m: models.Movie = models.Movie.objects.filter(
                title_ru=movie.get("title_ru"), title_eng=movie.get("title_eng")
            ).first()
            buttons.append(
                InlineKeyboardButton(
                    m.title,
                    callback_data=str(Route("movie", m.id, p=current)),
                )
            )

        keyboard = PaginationKeyboard.from_pagination(
            buttons, page=current, path="movie/pagination?p="
        )
        keyboard = append_button(
            keyboard, [
                InlineKeyboardButton("Меню фильмов", callback_data="movie/"),
            ]
        )

        return self.publish_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption=f"Фильмы, страница {current}"),
            keyboard=keyboard,
        )

    @router.add_method(r"movie/(\d+)\?p=(\d+)$")
    def movie(self, movie_id: int, page: int, *_):
        page = int(page)
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        description = ''
        for d in langs:  # type: Movie
            if d.desc:
                description = d.desc
                break

        buttons = [
            InlineKeyboardButton(
                models.Langs.repr(m.lang),
                callback_data=str(Route("movie", str(m.id), l=m.lang, p=page)),
            )
            for m in langs
        ]
        buttons.append(
            InlineKeyboardButton(
                f"Выбор фильма, страница {page}",
                callback_data=str(Route("movie", "pagination", p=page)),
            )
        )

        keyboard = InlineKeyboardMarkup.from_column(buttons)
        return self.publish_message(
            media=InputMediaPhoto(media=movie.poster or settings.MAIN_PHOTO, caption=f"{movie.title}\n\n{description}"),
            keyboard=keyboard,
        )

    @router.add_method(r"movie/(\d+)\?l=(\w+)&p=(\d+)$")
    def concrete_movie(self, movie_id: int, lang: str, page: int = 1, *_):
        movie = models.Movie.objects.get(id=movie_id)
        langs = models.Movie.objects.filter(
            title_ru=movie.title_ru, title_eng=movie.title_eng
        )
        movie = langs.get(lang=lang)

        buttons = [
            InlineKeyboardButton(
                f"[ {models.Langs.repr(mov.lang)} ]" if mov.lang == lang else models.Langs.repr(mov.lang),
                callback_data=str(Route("movie", mov.id, l=mov.lang, p=page)),
            )
            for mov in langs
        ]
        buttons.append(
            InlineKeyboardButton(
                f"Список фильмов, страница {page}",
                callback_data=str(Route("movie", "pagination", p=page)),
            )
        )
        rule = VideoRule(self.context.bot, self.update.effective_user.id)
        if not rule.user_is_subscribed():
            rule.need_subscribe(self.sender)
            return

        self.publish_message(
            media=InputMediaVideo(
                media=movie.file_id,
                caption=movie.title,
            ),
            keyboard=InlineKeyboardMarkup.from_column(buttons),
        )

    @router.add_method(r'delete/$')
    def _del(self):
        self.sender.delete()

    @functools.lru_cache
    def search(self, query: str) -> List[InlineQueryResultArticle]:
        """Метод поиска."""
        qs = Movie.objects.filter(
            Q(title_eng__icontains=query) | Q(title_ru_upper__contains=query.upper())
        )

        result = []
        for movie in qs[:49]:
            keyboard = InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    movie.title,
                    callback_data=str(Route("movie", movie.id, p=1)),
                )
            )
            path = Route("movie", movie.id, p=1).b64encode()
            article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{movie.title} {movie.lang}",
                thumb_url=settings.MAIN_PHOTO,
                photo_url=settings.MAIN_PHOTO,
                description="Киношка",
                reply_markup=keyboard,
                input_message_content=InputTextMessageContent(
                    f"Фильм {movie.title}:\n\n"
                    f"Постоянная ссылка: {self.context.bot.get_me().link}?start={path}"
                )
            )
            result.append(article)

        return result
