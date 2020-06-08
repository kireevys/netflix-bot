from math import ceil

from telegram import InlineKeyboardMarkup

from ..models import Series


class GridKeyboard(InlineKeyboardMarkup):
    @classmethod
    def from_grid(cls, grid_buttons, length=3, **kwargs):
        h = ceil(len(grid_buttons) / length)

        grid = []
        start = 0

        for i in range(h):
            stop = length * (i + 1)
            grid.append(grid_buttons[start:stop])
            start += length

        return cls(grid, **kwargs)


class SeriesKeyboard(GridKeyboard):
    def __init__(self, series: Series, inline_keyboard, **kwargs):
        super().__init__(inline_keyboard, **kwargs)
        self.series = series
