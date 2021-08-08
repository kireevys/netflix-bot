from django.conf import settings
from django.core.management.base import BaseCommand
from master.main import run


class Command(BaseCommand):
    help = "Master up"

    def check_env(self):
        if None in (
                settings.BOT_TOKEN,
                settings.MAIN_PHOTO,
                settings.UPLOADER_ID,
                settings.MOVIE_UPLOADER_ID,
        ):
            raise EnvironmentError("Check your ENV")

    def handle(self, *args, **options):
        self.check_env()
        run()
