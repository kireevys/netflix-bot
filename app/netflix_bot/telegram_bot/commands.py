import logging

from telegram import Update
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton
from ..models import User

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Покажи сериалы")]])

    user, created = User.get_or_create(update.effective_user)

    if created:
        logger.info(f"new user {user} created")

    logger.info(f"{user} say /start")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {user.user_name}. Я покажу тебе сериалы, только прикажи)",
        reply_markup=keyboard,
    )
