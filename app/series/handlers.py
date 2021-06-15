from telegram.ext import Filters, MessageHandler

from netflix_bot.telegram_bot.messages import SeriesUploadHandler

SERIES_GROUP = 1
series_filter = ~Filters.command  # & (Filters.chat(int(settings.SERIES_UPLOADER)))
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

handlers = [upload_series_h, series_add_description_h, series_add_poster_handler]
