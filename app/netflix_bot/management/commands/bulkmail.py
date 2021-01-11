import json
import logging
import time
from argparse import RawTextHelpFormatter
from datetime import datetime

import telegram
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher

from netflix_bot import models
from netflix_bot.my_lib import markdown

logger = logging.getLogger("bulkmail")


class Mail:
    def __init__(self, message: dict):
        self.mail = message

        self.keyboard = self.build_keyboard()
        self.picture = message.get("picture")
        self.text = markdown.escape(message.get("text"))

    def build(self):
        if self.picture:
            return self._picture()
        else:
            return self._raw()

    def _picture(self) -> dict:
        return dict(
            photo=self.picture,
            caption=self.text,
            parse_mode="MarkdownV2",
            reply_markup=self.keyboard,
        )

    def _raw(self):
        return dict(
            text=self.text,
            parse_mode="MarkdownV2",
            reply_markup=self.keyboard,
        )

    def build_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup([])

        for button in self.mail.get("keyboard"):
            button = InlineKeyboardButton(
                text=button.get("text"), url=button.get("link")
            )
            keyboard.inline_keyboard.append([button])

        return keyboard


class Command(BaseCommand):
    help = """Usage
           ./manage.py bulkmail -m=test -f=message.json"""

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("-m", "--mode", type=str, default="test")
        parser.add_argument("-f", "--file", type=str)

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

    def test_send(self, mail: Mail):
        for user_id in [362954912, 514312626]:
            self._send(user_id, mail)

    def bulkmail(self, mail: Mail):
        success = 0
        failed = 0
        new_unauth = 0

        qs = models.User.objects.filter(authorize=True)
        logger.info(f"Start on: {datetime.now()} | {len(qs)}")
        for num, user in enumerate(qs):
            if num % 30 == 0:
                time.sleep(0.005)

            try:
                self._send(user.user_id, mail)
                success += 1

            except telegram.error.Unauthorized:
                user.unauthorizing()
                new_unauth += 1
                failed += 1

            except telegram.error.TelegramError:
                failed += 1

        end_message = (
            f"success: {success}\n" f"failed: {failed}\n" f"new_unauth: {new_unauth}"
        )
        logger.info(end_message)

    def init(self):
        self.updater = Updater(token=settings.BOT_TOKEN, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def handle(self, *args, **options):
        self.check_env()
        self.init()

        mode = options.get("mode")
        file = options.get("file").replace("\\n", "\n")

        with open(file) as f:
            mail = Mail(json.load(f))

        if mode == "test":
            logger.info("Send test")
            self.test_send(mail)
        else:
            if input("Send all? y/n").strip() == "y":
                self.bulkmail(mail)
            else:
                logger.warning("Not sended")
