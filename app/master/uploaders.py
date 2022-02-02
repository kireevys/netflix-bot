import logging
from typing import Any

from django.conf import settings
from master.models import Slave
from master.share import MovieSharer, SeriesShare
from netflix_bot.models import Movie, Series
from netflix_bot.telegram_bot.managers.managers import MovieManager, SeriesManager
from netflix_bot.telegram_bot.uploaders import Uploader

logger = logging.getLogger("master")


class SeriesUploader(Uploader):
    uploader = settings.UPLOADER_ID
    manager = SeriesManager
    model = Series

    def after_upload(self, video: Any):
        sharer = SeriesShare(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share video {d} series")
            sharer.share(video, d.series)

    def after_description(self, desc_text: str):
        sharer = SeriesShare(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share description {d} series")
            sharer.share_description(desc_text, d.series)

    def after_poster(self, file_id: str):
        sharer = SeriesShare(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share poster {d} series")
            sharer.share_poster(self.update.channel_post.caption, file_id, d.series)


class MovieUploader(Uploader):
    uploader = settings.MOVIE_UPLOADER_ID
    manager = MovieManager
    model = Movie

    def after_upload(self, video: Any):
        sharer = MovieSharer(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share video {d} movies")
            sharer.share(video, d.movies)

    def after_description(self, desc_text: str):
        sharer = MovieSharer(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share description {d} movies")
            sharer.share_description(desc_text, d.movies)

    def after_poster(self, file_id: str):
        sharer = MovieSharer(settings.MASTER_TOKEN)
        slaves = Slave.objects.filter(enabled=True)
        for d in slaves:
            logger.info(f"Share poster {d} series")
            sharer.share_poster(self.update.channel_post.caption, file_id, d.series)
