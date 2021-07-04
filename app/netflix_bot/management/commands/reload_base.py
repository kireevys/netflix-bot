import logging
import re
from argparse import RawTextHelpFormatter
from datetime import datetime
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram.error import RetryAfter
from telegram.ext import Dispatcher, Updater

from netflix_bot import models
from netflix_bot.management.commands.bulkmail import Mail
from netflix_bot.telegram_bot.managers.series_manager import MovieManager, SeriesManager

logger = logging.getLogger("bulkmail")


class Command(BaseCommand):
    help = """Usage
           ./manage.py bulkmail -m=test -f=message.json"""

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    @staticmethod
    def check_env():
        if None in (
            settings.BOT_TOKEN,
            settings.MAIN_PHOTO,
            settings.UPLOADER_ID,
            settings.MOVIE_UPLOADER_ID,
        ):
            raise EnvironmentError("Check your ENV")

    def _send(self, user_id: int, mail: Mail):
        bot = self.dispatcher.bot
        if mail.picture:
            bot.send_photo(chat_id=user_id, **mail.build())
        else:
            bot.send_message(chat_id=user_id, **mail.build())

    def init(self):
        self.updater = Updater(token=settings.BOT_TOKEN, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def build_series_manager(self, episode: models.Episode):
        return SeriesManager(
            title_ru=episode.series.title_ru,
            title_eng=episode.series.title_eng,
            season=int(episode.season),
            episode=int(episode.episode),
            lang=episode.lang,
        )

    def build_movie_manager(self, movie: models.Movie):
        return MovieManager(
            title_ru=movie.title_ru,
            title_eng=movie.title_eng,
            lang=movie.lang,
        )

    def publish_series(self, episode: models.Episode):
        manager = self.build_series_manager(episode)
        try:
            self.dispatcher.bot.send_video(
                settings.UPLOADER_ID,
                episode.file_id,
                caption=manager.get_loader_format_caption(),
            )
        except RetryAfter as e:
            time = int(re.findall(r"\d+", str(e))[0])
            logger.info(f"Wait {time} second...")
            sleep(time)
            self.publish_series(episode)

    def publish_movie(self, movie: models.Movie):
        manager = self.build_movie_manager(movie)
        try:
            self.dispatcher.bot.send_video(
                settings.MOVIE_UPLOADER_ID,
                movie.file_id,
                caption=manager.get_loader_format_caption(),
            )
        except RetryAfter as e:
            time = int(re.findall(r"\d+", str(e))[0])
            logger.info(f"Wait {time} second...")
            sleep(time)
            self.publish_movie(movie)

    def reload_series(self):
        for i, episode in enumerate(models.Episode.objects.all()):
            if i % 300 == 0:
                logger.info(episode.id)
            self.publish_series(episode)

    def reload_movies(self):
        for i, movie in enumerate(models.Movie.objects.all()):
            if i % 300 == 0:
                logger.info(movie.id)
            self.publish_movie(movie)

    def handle(self, *args, **options):
        self.init()
        start = datetime.now()
        self.reload_series()
        logger.info((datetime.now() - start))
        self.reload_movies()
        logger.info((datetime.now() - start))
