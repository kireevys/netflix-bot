import json
from abc import abstractmethod

from telegram import InlineKeyboardButton

from netflix_bot.models import Series, Season, Episode


class AbsButton(InlineKeyboardButton):
    callback_type = None

    def __init__(self, **kwargs):
        if not self.callback_type:
            raise AttributeError("You can declare field callback_type")

        super().__init__(
            text=self.get_text(), callback_data=self.get_callback(), **kwargs
        )
        del self.__dict__[self.callback_type]

        self.__delete_extra()

    @abstractmethod
    def get_callback(self) -> str:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    def __delete_extra(self):
        """
        Удаление дополнительных полей из словаря
        """
        pass

    def __str__(self):
        return f"{self.callback_type}: {self.get_text()}: {self.get_callback()}"


class SeriesButton(AbsButton):
    callback_type = "series"

    def __init__(self, series: Series, **kwargs):
        self.series = series
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self.series.id, "type": self.callback_type})

    def get_text(self) -> str:
        return self.series.title


class BackButton(SeriesButton):
    def get_text(self) -> str:
        return f"К списку сезонов {self.series.title}"


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


class FilmListButton(AbsButton):
    callback_type = "film_list"

    def __init__(self, page, **kwargs):
        self.film_list = page
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"type": self.callback_type, "page": self.film_list})

    def get_text(self) -> str:
        return "Вернуться к списку сериалов"


class NavigateButton(AbsButton):
    callback_type = "navigate"
    LEFT = ">>"
    RIGHT = "<<"
    _side_repr = {LEFT: LEFT, RIGHT: RIGHT}

    def __init__(self, side, current, **kwargs):
        self.navigate = side
        self.current = current
        super().__init__(**kwargs)

    def __delete_extra(self):
        del self.__dict__["current"]

    def get_text(self) -> str:
        return self._side_repr[self.navigate]

    def get_callback(self) -> str:
        return json.dumps(
            {
                "navigate": self.navigate,
                "current": self.current,
                "type": NavigateButton.callback_type,
            }
        )


class EpisodeButton(AbsButton):
    callback_type = "episode"

    def __init__(self, episode: Episode, **kwargs):
        self.episode = episode
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self.episode.id, "type": self.callback_type})

    def get_text(self) -> str:
        return f"{self.episode.episode}"
