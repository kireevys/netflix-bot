from django.conf import settings
from netflix_bot.telegram_bot.messages import MovieUploadHandler, SeriesUploadHandler
from telegram.ext import Dispatcher, Filters, MessageHandler, Updater


def run():
    if not settings.BOT_TOKEN:
        raise EnvironmentError("Empty bot token")

    updater = Updater(token=settings.BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    # Uploaders
    # Series
    SERIES_GROUP = 1
    series_filter = (~Filters.command) & (
        Filters.chat(int(settings.UPLOADER_ID)))

    upload_series_h = MessageHandler(
        Filters.video & series_filter,
        SeriesUploadHandler.upload,
    )

    series_add_description_h = MessageHandler(
        Filters.reply & series_filter, SeriesUploadHandler.add_description
    )
    series_add_poster_handler = MessageHandler(
        Filters.photo & series_filter, SeriesUploadHandler.add_poster
    )

    dispatcher.add_handler(upload_series_h, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_poster_handler, group=SERIES_GROUP)
    dispatcher.add_handler(series_add_description_h, group=SERIES_GROUP)
    # Movies
    MOVIES_GROUP = 2
    movie_filter = (
        Filters.chat(chat_id=int(settings.MOVIE_UPLOADER_ID)
                     ) & ~Filters.command
    )
    movie_upload_h = MessageHandler(
        Filters.video & movie_filter,
        MovieUploadHandler.upload,
    )

    movie_add_description_h = MessageHandler(
        Filters.reply & movie_filter, MovieUploadHandler.add_description
    )
    movie_add_poster_handler = MessageHandler(
        Filters.photo & movie_filter, MovieUploadHandler.add_poster
    )

    dispatcher.add_handler(movie_upload_h, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_poster_handler, group=MOVIES_GROUP)
    dispatcher.add_handler(movie_add_description_h, group=MOVIES_GROUP)
