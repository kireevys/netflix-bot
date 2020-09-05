import json
from abc import abstractmethod

from telegram import InlineKeyboardButton

from netflix_bot.models import Series, Season, Episode, Genre


class AbsButton(InlineKeyboardButton):
    _callback_type = None

    def __init__(self, **kwargs):
        if not self._callback_type:
            raise AttributeError("You can declare field callback_type")

        super().__init__(
            text=kwargs.pop("text", self.get_text()),
            callback_data=self.get_callback(),
            **kwargs,
        )

    @abstractmethod
    def get_callback(self) -> str:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    def __str__(self):
        return f"{self._callback_type}: {self.get_text()}: {self.get_callback()}"


class SeriesButton(AbsButton):
    _callback_type = "series"

    def __init__(self, series: Series, **kwargs):
        self._series = series
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._series.id, "type": self._callback_type})

    def get_text(self) -> str:
        return self._series.title


class BackButton(SeriesButton):
    def get_text(self) -> str:
        return f"К списку сезонов {self._series.title}"


class SeasonButton(AbsButton):
    _callback_type = "season"

    def __init__(self, season: Season, **kwargs):
        self._season = season
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps(
            {
                "id": self._season.id,
                "series": self._season.series,
                "lang": self._season.lang,
                "type": self._callback_type,
            }
        )

    def get_text(self) -> str:
        return f"{self._season.id:<3}: {self._season.lang}"


class ShowSeriesButton(AbsButton):
    _callback_type = "series_list"

    def __init__(self, page, **kwargs):
        self._series_list = page
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type, "page": self._series_list})

    def get_text(self) -> str:
        return "Все сериалы"


class NavigateButton(AbsButton):
    _callback_type = "navigate"
    LEFT = ">>"
    RIGHT = "<<"
    _side_repr = {LEFT: LEFT, RIGHT: RIGHT}

    def __init__(self, side, current, **kwargs):
        self._navigate = side
        self._current = current
        super().__init__(**kwargs)

    def __delete_extra(self):
        del self.__dict__["current"]

    def get_text(self) -> str:
        return self._side_repr[self._navigate]

    def get_callback(self) -> str:
        return json.dumps(
            {
                "navigate": self._navigate,
                "current": self._current,
                "type": NavigateButton._callback_type,
            }
        )


class EpisodeButton(AbsButton):
    _callback_type = "episode"

    def __init__(self, episode: Episode, **kwargs):
        self._episode = episode
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._episode.id, "type": self._callback_type})

    def get_text(self) -> str:
        return f"{self._episode.episode}"


class AllGenresButton(AbsButton):
    _callback_type = "all_genres"

    def __init__(self, **kwargs):
        self._all_genres = None
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type})

    def get_text(self) -> str:
        return "Выбрать жанр"


class GenresButton(AbsButton):
    _callback_type = "genre"

    def __init__(self, genre: Genre, **kwargs):
        self._genre = genre
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._genre.id, "type": self._callback_type})

    def get_text(self) -> str:
        return str(self._genre)


class SeriesMainButton(AbsButton):
    _callback_type = "series_main"

    def get_text(self) -> str:
        return "Главное меню сериалов"

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type})
