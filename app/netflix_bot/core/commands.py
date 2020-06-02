from telegram import Update
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton


def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Покажи фильмы")]])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!",
        reply_markup=keyboard,
    )
