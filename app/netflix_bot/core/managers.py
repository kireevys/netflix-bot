import re
from math import ceil

from .. import models
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class GridKeyboard(InlineKeyboardMarkup):
    @classmethod
    def from_grid(cls, grid_buttons, l=3, **kwargs):
        h = ceil(len(grid_buttons) / l)

        grid = []
        start = 0

        for i in range(h):
            stop = l * (i + 1)
            grid.append(grid_buttons[start:stop])
            start += l

        return cls(grid, **kwargs)


class SeriesManager(dict):
    @classmethod
    def parse_caption(cls, caption) -> "SeriesManager":
        """
        Caption example:
            Неортодоксальная / Unorthodox
            1 Сезон / 4 Серия
            SUB
        """
        title, series, *lang = caption.split("\n")
        season, episode = re.findall(r"(\d+)", series)

        lang = lang[0].upper() if lang else models.Episode.Langs.RUS
        return cls(title=title, season=season, episode=episode, lang=lang)

    def __init__(self, title, season, episode, lang):
        self.title = title
        self.season = season
        self.episode = episode
        self.lang = lang
        super().__init__(title=title, season=season, episode=episode, lang=lang)

    def write(self, file_id, message_id):
        series, _ = models.Series.objects.get_or_create(title=self.title)
        episode = models.Episode.objects.create(
            series=series,
            season=self.season,
            episode=self.episode,
            lang=self.lang,
            file_id=file_id,
            message_id=message_id,
        )
        return episode
