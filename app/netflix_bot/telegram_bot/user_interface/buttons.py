import json
from abc import abstractmethod

from telegram import InlineKeyboardButton

from netflix_bot.models import Series, Season, Episode, Genre, Movie

_grid = {}


def grid(name):
    def wrapper(cls):
        _grid.update({name: cls})
        return cls

    return wrapper


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


@grid("series")
class SeriesButton(AbsButton):
    _callback_type = "series"

    def __init__(self, series: Series, **kwargs):
        self._series = series
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._series.id, "type": self._callback_type})

    def get_text(self) -> str:
        return self._series.title


@grid("movie")
class MovieButton(SeriesButton):
    _callback_type = "movies"


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


class ShowMoviesButton(AbsButton):
    _callback_type = "movies_list"

    def __init__(self, page, **kwargs):
        self._movies_list = page
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type, "page": self._movies_list})

    def get_text(self) -> str:
        return "Все фильмы"


class NavigateButton(AbsButton):
    _callback_type = "navigate"
    LEFT = ">>"
    RIGHT = "<<"
    CURRENT = "cur"
    NAVIGATE = "nav"
    _side_repr = {LEFT: LEFT, RIGHT: RIGHT}

    def __init__(self, side, current, grid_type="series", **kwargs):
        self._navigate = side
        self._current = current
        self._grid = grid_type
        super().__init__(**kwargs)

    def get_text(self) -> str:
        return self._side_repr[self._navigate]

    def get_callback(self) -> str:
        return json.dumps(
            {
                self.NAVIGATE: self._navigate,
                self.CURRENT: self._current,
                "grid": self._grid,
                "type": self._callback_type,
            }
        )


class NavigateMovie(NavigateButton):
    _callback_type = "nav_mv"


class EpisodeButton(AbsButton):
    _callback_type = "episode"

    def __init__(self, episode: Episode, **kwargs):
        self._episode = episode
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._episode.id, "type": self._callback_type})

    def get_text(self) -> str:
        return f"{self._episode.episode}"


class WatchMovieButton(AbsButton):
    _callback_type = "movie"

    def __init__(self, movie: Movie, **kwargs):
        self._movie = movie
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._movie.id, "type": self._callback_type})

    def get_text(self) -> str:
        return self._movie.title


class AllGenresButton(AbsButton):
    _callback_type = "all_genres"

    def __init__(self, **kwargs):
        self._all_genres = None
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type})

    def get_text(self) -> str:
        return "Выбрать жанр"


class MovieGenres(AllGenresButton):
    _callback_type = "all_mv_genres"


class GenresButton(AbsButton):
    _callback_type = "genre"

    def __init__(self, genre: Genre, **kwargs):
        self._genre = genre
        super().__init__(**kwargs)

    def get_callback(self) -> str:
        return json.dumps({"id": self._genre.id, "type": self._callback_type})

    def get_text(self) -> str:
        return str(self._genre)


class MovieGenre(GenresButton):
    _callback_type = "genre_mv"


class SeriesMainButton(AbsButton):
    _callback_type = "series_main"

    def get_text(self) -> str:
        return "Главное меню сериалов"

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type})


class MovieMainButton(AbsButton):
    _callback_type = "movies_main"

    def get_text(self) -> str:
        return "Главное меню фильмов"

    def get_callback(self) -> str:
        return json.dumps({"type": self._callback_type})
