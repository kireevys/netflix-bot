from telegram import InlineKeyboardButton, InlineKeyboardMarkup

START_MESSAGE = (
    "Смотри весь список фильмов и сериалов, "
    "используя кнопки ниже или воспользуйся поиском 🔍"
)

MAIN_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Все фильмы", callback_data="movie/")],
        [InlineKeyboardButton("Все сериалы", callback_data="series/")],
        [InlineKeyboardButton("Поиск", switch_inline_query_current_chat="")],
    ]
)
