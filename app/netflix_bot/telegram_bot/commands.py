import logging

from django.conf import settings
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from .user_interface.buttons import (
    MovieMainButton,
    SeriesMainButton,
    SearchSeries,
    SearchMovies,
)
from ..models import User

logger = logging.getLogger(__name__)

START_COMMAND = "start"


def build_keyboard(search_string):
    keyboard = InlineKeyboardMarkup(
        [
            [SearchSeries(search_string)],
            [SearchMovies(search_string)],
        ]
    )

    return keyboard


def search(update: Update, context: CallbackContext):
    search_string = update.effective_message.text[:28]
    keyboard = build_keyboard(search_string)

    context.bot.send_photo(
        photo=settings.MAIN_PHOTO,
        chat_id=update.effective_chat.id,
        caption=f"Вы ищете: \n{search_string}\nСтрока может быть обрезана - так надо",
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

    about_search = "Ты можешь воспользоваться поиском: просто напиши мне сообщение" \
                   "\n\nПока что я могу искать только по <b>английским названиям</b>" \
                   "\n\nВводи часть названия, например - напиши <b>harry</b>, и я покажу тебе все," \
                   "что подходит)"

    name = user.user_name or user.first_name or "Странник"
    context.bot.send_photo(
        parse_mode='HTML',
        photo=settings.MAIN_PHOTO,
        chat_id=update.effective_chat.id,
        caption=f"Привет, {name}. Ты находишься в главном меню\n\n{about_search}",
        reply_markup=keyboard,
    )
