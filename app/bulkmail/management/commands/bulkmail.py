import json
import logging
from argparse import RawTextHelpFormatter

from django.core.management import BaseCommand, CommandParser

from bulkmail.message import Button, Message
from bulkmail.sender import Builkmail, TelegramSender
from netflix_bot import models

logger = logging.getLogger()


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

    def reader(self, filename: str) -> Message:
        with open(filename) as f:
            return Message(**json.load(f))

    def handle(self, *args, **options):
        message = Message(
            "Развлекаюсь как могу",
            [Button("some", "http://google.com")],
            "https://cdnb.artstation.com/p/assets/images/images/011/435/375/large/gerardo-de-lara-this-is-fine.jpg?1529567764",
        )
        sender = TelegramSender()

        if options.get("mode") == "test":
            logger.info("Send test")
            sender.send(message, 362954912)
        else:
            if input("Send all? y/n ") == "y":
                users = models.User.objects.filter(authorize=True)
                Builkmail().bulk(message, users, sender)
            else:
                logger.warning("Not sended")
