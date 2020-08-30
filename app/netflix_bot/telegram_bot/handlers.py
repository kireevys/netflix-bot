import logging

from django.conf import settings
from telegram import Update
from telegram.ext import CallbackContext

from netflix_bot.telegram_bot.user_interface.keyboards import get_factory

logger = logging.getLogger(__name__)


def get_film_list(update: Update, context: CallbackContext):
    factory = get_factory()

    logger.info(f"{update.effective_user} request films list")

    keyboard = factory.page_from_column(1)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=settings.MAIN_PHOTO,
        reply_markup=keyboard,
    )
