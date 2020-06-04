from telegram import Update
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton


def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Покажи сериалы")]])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет. Я покажу тебе сериалы, только прикажи)",
        reply_markup=keyboard,
    )
