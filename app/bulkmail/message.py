from dataclasses import dataclass
from typing import List, Optional, TypedDict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bulkmail.sender import Mail
from netflix_bot.my_lib import markdown


class Picture(TypedDict):
    photo: str
    caption: str
    reply_markup: InlineKeyboardMarkup
    parse_mode: str


class Raw(TypedDict):
    text: str
    reply_markup: InlineKeyboardMarkup
    parse_mode: str


@dataclass
class Button:
    text: str
    url: str


class Message(Mail):
    def __init__(
        self,
        text: str,
        buttons: List[Button],
        media: Optional[str] = None,
    ):
        self.keyboard = self._build_keyboard(buttons)
        self.text = markdown.escape(text)
        self.media = media

    def build(self) -> dict:
        if self.media:
            return self._picture()
        else:
            return self._raw()

    def _picture(self) -> Picture:
        return Picture(
            photo=self.media,
            caption=self.text,
            parse_mode="MarkdownV2",
            reply_markup=self.keyboard,
        )

    def _raw(self) -> dict:
        return Raw(
            text=self.text,
            parse_mode="MarkdownV2",
            reply_markup=self.keyboard,
        )

    def _build_keyboard(self, buttons: List[Button]) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text=button.text, url=button.url)
                for button in buttons
            ]]
        )

