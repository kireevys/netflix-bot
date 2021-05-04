from django.conf import settings
from telegram.ext import Filters, MessageHandler

from netflix_bot.telegram_bot.messages import MovieUploadHandler

movie_filter = (~Filters.command) & Filters.chat(
    chat_id=int(settings.MOVIE_UPLOADER_ID)
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

handlers = [movie_upload_h, movie_add_description_h, movie_add_poster_handler]
