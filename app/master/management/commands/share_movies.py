import logging
import re
from time import sleep

from django.conf import settings
from django.core.management import BaseCommand, CommandParser
from master.share import MovieSharer
from netflix_bot import models
from telegram.error import RetryAfter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Share movie to channel"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("-d", "--destination", type=str)

    def check_env(self):
        if None in (
                settings.BOT_TOKEN,
                settings.MAIN_PHOTO,
                settings.UPLOADER_ID,
                settings.MOVIE_UPLOADER_ID,
        ):
            raise EnvironmentError("Check your ENV")

    def handle(self, destination, *args, **options):
        self.check_env()
        sharer = MovieSharer(settings.BOT_TOKEN)
        for i in self._get_movies():
            try:
                sharer.share(i, destination)
            except RetryAfter as e:
                time = int(re.findall(r"\d+", str(e))[0])
                logger.info(f"Wait {time} second...")
                sleep(time)
                sharer.share(i, destination)

    def _get_movies(self):
        return models.Movie.objects.all()
