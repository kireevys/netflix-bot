from master.uploaders import MovieUploader, SeriesUploader
from telegram import Update
from telegram.ext import CallbackContext


class UploadHandler:
    uploader = None

    @classmethod
    def add_description(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).add_description(
            update.effective_message.text)

    @classmethod
    def add_poster(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).add_poster(
            update.channel_post.photo[-1].file_id)

    @classmethod
    def upload(cls, update: Update, context: CallbackContext):
        cls.uploader(update, context).upload()


class SeriesUploadHandler(UploadHandler):
    uploader = SeriesUploader


class MovieUploadHandler(UploadHandler):
    uploader = MovieUploader
