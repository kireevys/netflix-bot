from django.conf import settings
from telegram import Bot

ME = Bot(settings.BOT_TOKEN).get_me()
