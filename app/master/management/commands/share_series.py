import logging
import re
from time import sleep

from django.conf import settings
from django.core.management import BaseCommand, CommandParser
from master.share import SeriesShare
from netflix_bot import models
from telegram.error import RetryAfter

logger = logging.getLogger("master")


class Command(BaseCommand):
    help = "Share series to channel"

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

    def _wait_retry(self, error_text):
        time = int(re.findall(r"\d+", str(error_text))[0])
        logger.info(f"Wait {time} second...")
        sleep(time)

    def handle(self, destination, *args, **options):
        self.check_env()
        sharer = SeriesShare(settings.BOT_TOKEN)
        for i in self._get_videos():
            try:
                sharer.share(i, destination)
            except RetryAfter as e:
                self._wait_retry(str(e))
                sharer.share(i, destination)

    def _get_videos(self):
        return models.Episode.objects.all()
