from abc import ABC, abstractmethod
from typing import Any

from netflix_bot import models
from netflix_bot.telegram_bot.managers.managers import MovieManager, SeriesManager
from telegram import Bot


class Share(ABC):
    def __init__(self, credentials: str):
        self.sender = Bot(credentials)

    @abstractmethod
    def share(self, video: Any, destination: int) -> bool:
        ...

    @abstractmethod
    def share_description(self, description: str, destination: int) -> bool:
        ...

    @abstractmethod
    def share_poster(self, video: Any, poster: str, destination: int) -> bool:
        ...


class MovieSharer(Share):
    def share(self, video: models.Movie, destination: int) -> bool:
        manager = MovieManager(
            title_ru=video.title_ru,
            title_eng=video.title_eng,
            lang=video.lang,
        )
        self.sender.send_video(
            destination, video.file_id, caption=manager.get_loader_format_caption()
        )
        return True

    def share_description(self, description: str, destination: int) -> bool:
        self.sender.send_message(destination, description)
        return True

    def share_poster(self, title: str, poster: str, destination: int) -> bool:
        self.sender.send_photo(destination, poster, title)
        return True


class SeriesShare(Share):
    def share(self, video: models.Episode, destination: int) -> bool:
        manager = SeriesManager(
            title_ru=video.series.title_ru,
            title_eng=video.series.title_eng,
            season=int(video.season),
            episode=int(video.episode),
            lang=video.lang,
        )
        self.sender.send_video(
            destination, video.file_id, caption=manager.get_loader_format_caption()
        )
        return True

    def share_description(self, description: str, destination: int) -> bool:
        self.sender.send_message(destination, description)
        return True

    def share_poster(self, title: str, poster: str, destination: int) -> bool:
        self.sender.send_photo(destination, poster, title)
        return True
