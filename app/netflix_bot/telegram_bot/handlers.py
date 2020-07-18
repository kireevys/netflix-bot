from telegram import Update
from telegram.ext import CallbackContext

from netflix_bot import models
from netflix_bot.telegram_bot.ui import SeriesButton, PaginationKeyboardFactory


def get_factory(per_page: int = 5):
    all_videos = models.Series.objects.all()

    buttons = [SeriesButton(series) for series in all_videos]

    factory = PaginationKeyboardFactory(buttons, per_page)
    return factory


def get_film_list(update: Update, context: CallbackContext):
    factory = get_factory()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что у меня есть",
        reply_markup=factory.page_from_column(1),
    )
