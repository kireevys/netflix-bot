import logging
import time
from argparse import RawTextHelpFormatter

import telegram
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher

from netflix_bot import models

logger = logging.getLogger("project")


class Command(BaseCommand):
    help = """Usage
           ./manage.py bulkmail -u 362954912 -m=all -ln=СКАЧАТЬ -l=https://t.me/softwareBoxRu/363 -f=data.md"""

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("-u", "--user_id", type=int, nargs="+")
        parser.add_argument("-m", "--mode", type=str, default="one")
        parser.add_argument("-l", "--link", type=str)
        parser.add_argument("-ln", "--link-name", type=str, default="ТЫЦ!")
        # parser.add_argument("-t", "--text", type=str)
        parser.add_argument("-f", "--file", type=str)

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def check_env(self):
        if None in (
            settings.BOT_TOKEN,
            settings.MAIN_PHOTO,
            settings.UPLOADER_ID,
            settings.MOVIE_UPLOADER_ID,
        ):
            raise EnvironmentError("Check your ENV")

    def one(self, user_id: int, message: str, keyboard: InlineKeyboardMarkup):
        self.dispatcher.bot.send_message(
            chat_id=user_id, text=message, reply_markup=keyboard
        )

    def bulkmail(self, message, keyboard: InlineKeyboardMarkup):
        for num, user in enumerate(models.User.objects.all()):
            if num % 30 == 0:
                time.sleep(0.05)

            try:
                self.dispatcher.bot.send_message(
                    chat_id=user.user_id, text=message, reply_markup=keyboard
                )
                logger.info(
                    "Success send", extra={"user_id": user.user_id, "user": user.id}
                )
                if not user.authorize:
                    user.authorizing()

            except telegram.error.Unauthorized:
                user.unauthorizing()
                logger.info("User unauthorized", extra={"user_id": user.user_id})
            except telegram.error.TelegramError as e:
                logger.warning(
                    "Cant send to user",
                    extra={"exception": str(e), "user_id": user.user_id},
                )

    def init(self):
        self.updater = Updater(token=settings.BOT_TOKEN, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def handle(self, *args, **options):
        self.check_env()
        self.init()
        print(options)

        button = (
            InlineKeyboardButton(text=options.get("link_name"), url=options.get("link"))
            if options.get("link")
            else None
        )
        keyboard = InlineKeyboardMarkup([[button]])
        print(keyboard)
        mode = options.get("mode")
        print(mode)

        file = options.get("file").replace("\\n", "\n")

        with open(file) as f:
            text = f.read()

        if mode == "one":
            users = options.get("user_id")

            if not users:
                raise AttributeError("not user id")

            for user_id in users:
                self.one(user_id, text, keyboard)
        else:
            self.bulkmail(text, keyboard)
