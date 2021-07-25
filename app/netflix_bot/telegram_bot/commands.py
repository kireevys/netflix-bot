import binascii
import logging
from enum import Enum

from telegram import Update
from telegram.ext import CallbackContext

from ..models import Referral, User
from .managers.movie import MovieCallback
from .managers.series import SeriesCallback
from .senders import InlineSender
from .user_interface.callbacks import CallbackManager
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
    manager = MovieCallback(update, context, InlineSender(update, context))
    user, created = User.get_or_create(update.effective_user)

    if not context.args:
        return manager.root()

    # Если есть аргументы, то это либо путь, либо рефералка.
    if not handle_path(context.args[0], manager):
        # Если это не путь, значит рефералка.
        # Рефералов считает только для новых юзеров
        if not created:
            Referral.add(context.args[0], user)

        return manager.root()


def handle_path(args: str, manager: CallbackManager) -> bool:
    try:
        query = Route.b64decode(args)
    except (binascii.Error, UnicodeDecodeError):
        return False

    handler, args = router.get_handler(query)
    handler(manager, *args)
    return True
