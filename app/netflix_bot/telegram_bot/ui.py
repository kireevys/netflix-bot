import json
from abc import abstractmethod
from math import ceil
from typing import Collection

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from netflix_bot.models import Series, Episode, Season


class GridKeyboard(InlineKeyboardMarkup):
    @classmethod
    def from_grid(
        cls, grid_buttons: Collection[InlineKeyboardButton], length=3, **kwargs
    ):
        h = ceil(len(grid_buttons) / length)

        grid = []
        start = 0

        for i in range(h):
            stop = length * (i + 1)
            grid.append(grid_buttons[start:stop])
            start += length

        return cls(grid, **kwargs)


class AbsButton(InlineKeyboardButton):
    callback_type = None

    def __init__(self, **kwargs):
        if not self.callback_type:
            raise AttributeError("You can declare field callback_type")

        super().__init__(
            text=self.get_text(), callback_data=self.get_callback(), **kwargs
        )
        del self.__dict__[self.callback_type]

    @abstractmethod
    def get_callback(self) -> str:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass


class SeriesButton(AbsButton):
    callback_type = "series"

    def __init__(self, series: Series, **kwargs):
        self.series = series
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self.series.id, "type": "series"})

    def get_text(self) -> str:
        return self.series.title


class SeasonButton(AbsButton):
    callback_type = "season"

    def __init__(self, season: Season, **kwargs):
        self.season = season
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps(
            {
                "id": self.season.id,
                "series": self.season.series,
                "lang": self.season.lang,
                "type": self.callback_type,
            }
        )

    def get_text(self) -> str:
        return f"{self.season.id:<3}: {self.season.lang}"


class EpisodeButton(AbsButton):
    callback_type = "episode"

    def __init__(self, episode: Episode, **kwargs):
        self.episode = episode
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self.episode.id, "type": self.callback_type})

    def get_text(self) -> str:
        return f'{self.episode.episode}'


class PaginationKeyboard(GridKeyboard):
    def __init__(self, inline_keyboard, **kwargs):
        super().__init__(inline_keyboard, **kwargs)

    def next(self):
        pass

    def previous(self):
        pass
