from math import ceil
from typing import Collection, List

from django.core.paginator import Paginator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class GridKeyboard(InlineKeyboardMarkup):
    @classmethod
    def _get_grid(cls, grid_buttons: Collection[InlineKeyboardButton], length=3):
        h = ceil(len(grid_buttons) / length)

        grid = []
        start = 0

        for i in range(h):
            stop = length * (i + 1)
            grid.append(grid_buttons[start:stop])
            start += length

        return grid

    @classmethod
    def from_grid(
        cls, grid_buttons: Collection[InlineKeyboardButton], length=3, **kwargs
    ) -> InlineKeyboardMarkup:
        grid = cls._get_grid(grid_buttons, length)
        return cls(grid, **kwargs)


class PaginationKeyboard(InlineKeyboardMarkup):
    @classmethod
    def from_pagination(
        cls,
        buttons: Collection[InlineKeyboardButton],
        page: int,
        path: str,
        per_page=5,
        **kwargs,
    ) -> InlineKeyboardMarkup:
        p = Paginator(buttons, per_page)

        p_page = list(p.page(page))

        keyboard = cls.from_column(p_page, **kwargs)
        keyboard = append_button(keyboard, cls._get_navigator(page, p, path))

        return keyboard

    @staticmethod
    def _get_navigator(current_page, p: Paginator, path):
        navigator = []

        if current_page > 1:
            navigator.append(
                InlineKeyboardButton(
                    "<<", callback_data=f"{path}{current_page - 1}")
            )

        if current_page < len(p.page_range):
            navigator.append(
                InlineKeyboardButton(
                    ">>", callback_data=f"{path}{current_page + 1}")
            )

        return navigator


def append_button(
    keyboard: InlineKeyboardMarkup, buttons: List[InlineKeyboardButton]
) -> InlineKeyboardMarkup:
    keyboard.inline_keyboard.append(buttons)
    return keyboard
