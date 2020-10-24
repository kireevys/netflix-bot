import logging

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import Update
from telegram.ext import CallbackContext

from .managers.movies_manager import MoviesCallback
from .managers.series_manager import SeriesCallback
from ..models import User

logger = logging.getLogger(__name__)

SERIES_START = "Cериалы"
MOVIES_START = "Фильмы"
MOVIES_SEARCH = "movies"
SERIES_SEARCH = "series"
START_COMMAND = "start"


def movies_search(update: Update, context: CallbackContext):
    title_eng = ' '.join(context.args)
    manager = MoviesCallback(update, context)
    manager.search(title_eng)


def series_search(update: Update, context: CallbackContext):
    title_eng = ' '.join(context.args)
    manager = SeriesCallback(update, context)
    manager.search(title_eng)


def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton(SERIES_START)],
            [KeyboardButton(MOVIES_START)],
        ],
        one_time_keyboard=True,
    )

    user, created = User.get_or_create(update.effective_user)

    if created:
        logger.info(f"new user {user} created")

    logger.info(f"{user} say /start")

    name = user.user_name or user.first_name or "Странник"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {name}. Я покажу тебе сериалы, только прикажи)",
        reply_markup=keyboard,
    )
