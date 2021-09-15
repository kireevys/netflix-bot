import logging
from argparse import RawTextHelpFormatter

from bulkmail.models import Bulkmail, Button, Message
from bulkmail.senders import BulkmailSender
from django.conf import settings
from django.core.management.base import BaseCommand
from netflix_bot.models import User
from telegram import Bot

logger = logging.getLogger("bulkmail")


class Command(BaseCommand):
    help = """Usage
           ./manage.py run_bm -m=test"""

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

    def handle(self, *args, **options):
        self.check_env()
        bot = Bot(settings.BOT_TOKEN)
        sender = BulkmailSender(bot)
        message = Message.objects.create(
            text="Some text",
            buttons=[
                Button(text="First", link="http://google.com"),
                Button(text="Second", link="http://ya.ru"),
            ],
            content="https://ibb.co/51QbjcW",
            content_type=Message.ContentTypes.PHOTO,
        )
        bulkmail = Bulkmail.objects.create(message=message)
        users = User.objects.filter(pk=1)
        bulkmail.add_users(users)
        sender.run(bulkmail)
