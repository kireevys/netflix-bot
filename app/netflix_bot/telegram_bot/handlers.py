import logging

from django.conf import settings
from telegram import Update
from telegram.ext import CallbackContext

from netflix_bot import models
from netflix_bot.telegram_bot.ui import SeriesButton, PaginationKeyboardFactory

logger = logging.getLogger(__name__)


def get_factory(per_page: int = 5):
    all_videos = models.Series.objects.all().order_by('title')

    buttons = [SeriesButton(series) for series in all_videos]

    factory = PaginationKeyboardFactory(buttons, per_page)
    return factory


def get_film_list(update: Update, context: CallbackContext):
    factory = get_factory()

    logger.info(f"{update.effective_user} request f-list")

    keyboard = factory.page_from_column(1)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=settings.MAIN_PHOTO,
        reply_markup=keyboard,

    )
