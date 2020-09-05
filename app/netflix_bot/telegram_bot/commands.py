import logging

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import Update
from telegram.ext import CallbackContext

from ..models import User

logger = logging.getLogger(__name__)

SERIES_START = "Хочу сериал"
START_COMMAND = "start"


def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton(SERIES_START)],
        ],
        one_time_keyboard=True,
    )

    user, created = User.get_or_create(update.effective_user)

    if created:
        logger.info(f"new user {user} created")

    logger.info(f"{user} say /start")

    name = user.user_name or user.first_name or "Странник"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {name}. Я покажу тебе сериалы, только прикажи)",
        reply_markup=keyboard,
    )
