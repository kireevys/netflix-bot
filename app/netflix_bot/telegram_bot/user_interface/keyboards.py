from math import ceil
from typing import Collection

from django.core.paginator import Paginator
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from netflix_bot import models
from netflix_bot.telegram_bot.user_interface.buttons import NavigateButton, SeriesButton, SeriesMainButton


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
    ):
        grid = cls._get_grid(grid_buttons, length)
        return cls(grid, **kwargs)

    @classmethod
    def pagination(
            cls, grid_buttons: Collection[InlineKeyboardButton], per_page: int, page: int
    ):
        p = Paginator(grid_buttons, per_page)

        return p.page(page)


class PaginationKeyboardFactory:
    def __init__(self, grid_buttons: Collection[InlineKeyboardButton], per_page=5):
        self.grid_buttons = grid_buttons
        self.per_page = per_page

    def page_from_column(self, number: int) -> InlineKeyboardMarkup:
        p = Paginator(self.grid_buttons, self.per_page)
        keyboard = InlineKeyboardMarkup.from_column(p.page(number))
        navigator = self._get_navigator(number, p)

        keyboard.inline_keyboard.append(navigator)

        keyboard.inline_keyboard.append([SeriesMainButton()])

        return keyboard

    def page_from_grid(self, number: int) -> InlineKeyboardMarkup:
        p = Paginator(self.grid_buttons, self.per_page)
        keyboard = GridKeyboard.from_grid(p.page(number))

        navigator = self._get_navigator(number, p)

        keyboard.inline_keyboard.append(navigator)

        return keyboard

    def _get_navigator(self, current_page, p):
        navigator = []

        if current_page > 1:
            navigator.append(NavigateButton("<<", current_page - 1))

        if current_page < len(p.page_range):
            navigator.append(NavigateButton(">>", current_page + 1))

        return navigator


def get_factory(per_page: int = 5):
    all_videos = models.Series.objects.all().order_by("title_ru")

    buttons = [SeriesButton(series) for series in all_videos]

    factory = PaginationKeyboardFactory(buttons, per_page)
    return factory