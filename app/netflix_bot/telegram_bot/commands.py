import binascii
import logging
from enum import Enum

from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from .managers.movie import MovieCallback
from .managers.series import SeriesCallback
from .senders import InlineSender, MessageSender
from .user_interface.router import Route, router
from ..models import Referral, User

logger = logging.getLogger(__name__)

START_COMMAND = "start"


class Commands(Enum):
    START = "start"
    MOVIE = "movie"
    SERIES = "series"


def movie(update: Update, context: CallbackContext):
    MovieCallback(update, context, InlineSender(update, context)).main()


def series(update: Update, context: CallbackContext):
    SeriesCallback(update, context, InlineSender(update, context)).main()


def start(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Все фильмы", callback_data="movie/")],
            [InlineKeyboardButton("Все сериалы", callback_data="series/")],
        ]
    )

    user, created = User.get_or_create(update.effective_user)

    if created:
        logger.info(f"new user {user} created")

    logger.info(f"{user} say /start")

    about_search = (
        "Смотри весь список фильмов и сериалов, "
        "используя кнопки ниже или воспользуйся поиском,"
        f"напиши {context.bot.get_me().name} и начни искать."
    )
    if context.args:
        try:
            query = Route.b64decode(context.args[0])
            handler, args = router.get_handler(query)
            m = MovieCallback(update, context, InlineSender(update, context))
            handler(m, *args)
            return
        except (binascii.Error, UnicodeDecodeError):
            pass

    name = user.user_name or user.first_name or "Странник"
    MessageSender(update, context).send(
        photo=settings.MAIN_PHOTO,
        caption=f"Привет, {name}.\nТы находишься в главном меню\n\n{about_search}",
        keyboard=keyboard,
    )

    if context.args and created:
        Referral.add(context.args[0], user)
