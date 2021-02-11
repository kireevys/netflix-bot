import logging

from django.conf import settings
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from .user_interface.buttons import (
    MovieMainButton,
    SearchMovies,
    SearchSeries,
    SeriesMainButton,
)
from ..common import safe_encode
from ..models import Referral, User

logger = logging.getLogger(__name__)

START_COMMAND = "start"


def build_keyboard(search_string):
    return InlineKeyboardMarkup(
        [
            [SearchSeries(search_string)],
            [SearchMovies(search_string)],
        ]
    )


def search(update: Update, context: CallbackContext):
    search_string, text = safe_encode(update.effective_message.text[:28])
    keyboard = build_keyboard(search_string)

    context.bot.send_photo(
        photo=settings.MAIN_PHOTO,
        chat_id=update.effective_chat.id,
        caption=f"{text}\nВыбери - в какой категории искать:",
        reply_markup=keyboard,
    )


def start(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(
        [
            [MovieMainButton()],
            [SeriesMainButton()],
        ]
    )

    user, created = User.get_or_create(update.effective_user)

    if created:
        logger.info(f"new user {user} created")

    logger.info(f"{user} say /start")

    about_search = (
        "Смотри весь список фильмов и сериалов, "
        "используя кнопки ниже или воспользуйся поиском,"
        "просто напиши мне часть названия фильма или сериала."
    )

    name = user.user_name or user.first_name or "Странник"
    context.bot.send_photo(
        parse_mode="HTML",
        photo=settings.MAIN_PHOTO,
        chat_id=update.effective_chat.id,
        caption=f"Привет, {name}.\nТы находишься в главном меню\n\n{about_search}",
        reply_markup=keyboard,
    )

    if context.args:
        Referral.add(context.args[0], user)
