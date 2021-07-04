import logging
import uuid
from typing import List

from django.conf import settings
from django.db.models import Q
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputMediaPhoto,
    InputMediaVideo,
    InputTextMessageContent,
)

from netflix_bot import models
from netflix_bot.my_lib import markdown
from netflix_bot.telegram_bot.user_interface.callbacks import CallbackManager, VideoRule
from netflix_bot.telegram_bot.user_interface.keyboards import (
    GridKeyboard,
    PaginationKeyboard,
    append_button,
)
from netflix_bot.telegram_bot.user_interface.router import Route, router

logger = logging.getLogger()


class SeriesCallback(CallbackManager):
    @router.add_method(r"series/$")
    def main(self, *_):
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Список сериалов", callback_data="series/all/")],
                # [
                #     InlineKeyboardButton(
                #         "Сериалы по жанрам", callback_data="series/genre/"
                #     )
                # ],
            ]
        )
        return self.publish_message(
            media=InputMediaPhoto(media=settings.MAIN_PHOTO, caption="СЕРИАЛЫ"),
            keyboard=keyboard,
        )

    def search(self, query: str) -> List[InlineQueryResultArticle]:
        qs = models.Series.objects.filter(
            Q(title_eng__icontains=query) | Q(title_ru_upper__contains=query.upper())
        ).order_by("title_ru")

        result = []
        for series in qs[:49]:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            series.title,
                            callback_data=str(Route("series", str(series.id), p=1)),
                        )
                    ]
                ]
            )
            path = Route("series", series.id, p=1).b64encode()
            article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                caption=series.title,
                title=series.title,
                thumb_url=settings.MAIN_PHOTO,
                photo_url=settings.MAIN_PHOTO,
                description="Сериальчик",
                reply_markup=keyboard,
                input_message_content=InputTextMessageContent(
                    f"https://t.me/{self.context.bot.get_me().first_name}?start={path}"
                ),
            )
            result.append(article)

        return result

    @router.add_method(r"series/all/$")
    @router.add_method(r"series/pagination\?p=(\d+)")
    def all(self, page: str = 1):
        """
        Выбор сериала - возвращает сезоны
        """
        page = int(page)

        series = models.Series.objects.all()

        buttons = [
            InlineKeyboardButton(
                s.title, callback_data=str(Route("series", s.id, p=page))
            )
            for s in series
        ]

        keyboard = PaginationKeyboard.from_pagination(
            buttons, page=page, path="series/pagination?p="
        )
        keyboard = append_button(
            keyboard, [InlineKeyboardButton("Главная", callback_data="series/")]
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=settings.MAIN_PHOTO, caption="Вот что у меня есть"
            ),
            keyboard=keyboard,
        )

    @router.add_method(r"series/(\d+)\?l=(\w+)&p=(\d+)")
    def season(self, series_id, lang, page, *_):
        series = models.Series.objects.get(pk=series_id)

        lang_repr = models.Langs.repr(lang)

        buttons = [
            InlineKeyboardButton(
                f"Сезон {season.id}",
                callback_data=str(
                    Route("series", series_id, season.id, l=lang, p=page)
                ),
            )
            for season in series.get_seasons(lang)
        ]

        keyboard = GridKeyboard.from_column(buttons)
        append_button(
            keyboard,
            [
                InlineKeyboardButton(
                    "Изменить озучку",
                    callback_data=str(Route("series", series_id, p=page)),
                )
            ],
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO,
                caption=f"{series.title} {lang_repr}\n\n{series.desc or ''}",
            ),
            keyboard=keyboard,
        )

    @router.add_method(r"series/(\d+)\?p=(\d+)")
    def language(self, series_id: int, page: int = 1):
        """
        Возвращает Список доступных языков для сериала
        """
        series = models.Series.objects.get(pk=series_id)
        langs = series.get_languages()
        buttons = [
            InlineKeyboardButton(
                f"{models.Langs.repr(episode.lang)}",
                callback_data=str(Route("series", series_id, l=episode.lang, p=page)),
            )
            for episode in langs
        ]

        keyboard = GridKeyboard.from_column(buttons)
        append_button(
            keyboard,
            [
                InlineKeyboardButton(
                    "Список сериалов",
                    callback_data=str(Route("series", "pagination", p=page)),
                )
            ],
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO,
                caption=f"{series.title}\n\n{series.desc or ''}",
            ),
            keyboard=keyboard,
        )

    @router.add_method(r"series/(\d+)/(\d+)\?l=(\w+)&p=(\d+)")
    def publish_all_episodes_for_season(self, series_id, season_id, lang, page):
        """
        Список эпизодов сезона
        """
        episodes = models.Episode.objects.filter(
            series_id=series_id, season=season_id, lang=lang
        ).order_by("episode")

        buttons = [
            InlineKeyboardButton(
                episode.episode,
                callback_data=str(
                    Route(
                        "series", series_id, season_id, episode.episode, l=lang, p=page
                    )
                ),
            )
            for episode in episodes
        ]
        keyboard = GridKeyboard.from_grid(buttons)
        series = models.Series.objects.get(pk=series_id)

        append_button(
            keyboard,
            [
                InlineKeyboardButton(
                    "Список сезонов",
                    callback_data=str(Route("series", series_id, l=lang, p=page)),
                )
            ],
        )

        caption = (
            f"Список серий {series.title} {models.Langs.repr(lang)}\n Сезон {season_id}"
        )

        return self.publish_message(
            media=InputMediaPhoto(
                media=series.poster or settings.MAIN_PHOTO, caption=caption
            ),
            keyboard=keyboard,
        )

    @router.add_method(r"series/(\d+)/(\d+)/(\d+)\?l=(\w+)&p=(\d+)")
    def publish_episode(self, series_id, season_id, episode_id, lang, page) -> None:
        episode = models.Episode.objects.get(
            episode=episode_id, series_id=series_id, season=season_id, lang=lang
        )

        episode_index = f"Сезон {episode.season} Эпизод {episode.episode}"
        series_title = markdown.escape(episode.series.title)
        caption = f"{series_title}\n\n{episode_index} {models.Langs.repr(episode.lang)}"

        buttons = [
            InlineKeyboardButton(
                side,
                callback_data=str(
                    Route("series", series_id, season_id, ep.episode, l=lang, p=page)
                ),
            )
            for ep, side in (
                episode.get_previous(),
                (episode, f"[ {episode.episode} ]"),
                episode.get_next(),
            )
            if ep is not None
        ]

        keyboard = InlineKeyboardMarkup.from_row(buttons)
        append_button(
            keyboard,
            [
                InlineKeyboardButton(
                    "Выбор серии",
                    callback_data=str(
                        Route("series", series_id, season_id, l=lang, p=page)
                    ),
                )
            ],
        )
        rule = VideoRule(self.context.bot, self.update.effective_user.id)
        if rule.user_is_subscribed():
            rule.need_subscribe(self.sender)
            return

        return self.publish_message(
            media=InputMediaVideo(
                episode.file_id, caption=caption, parse_mode="MarkdownV2"
            ),
            keyboard=keyboard,
        )
