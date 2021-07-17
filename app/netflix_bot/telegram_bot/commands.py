import binascii
import logging
from enum import Enum

from telegram import Update
from telegram.ext import CallbackContext

from ..models import Referral, User
from .managers.movie import MovieCallback
from .managers.series import SeriesCallback
from .senders import InlineSender
from .user_interface.router import Route, router

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
    if context.args:
        try:
            query = Route.b64decode(context.args[0])
            handler, args = router.get_handler(query)
            m = MovieCallback(update, context, InlineSender(update, context))
            handler(m, *args)
            return
        except (binascii.Error, UnicodeDecodeError):
            pass
    else:
        MovieCallback(update, context, InlineSender(update, context)).root()

    user, created = User.get_or_create(update.effective_user)
    if context.args and created:
        logger.info(f"new user {user} created")
        Referral.add(context.args[0], user)
