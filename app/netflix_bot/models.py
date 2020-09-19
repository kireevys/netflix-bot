# Create your models here.

from django.db import models
from django.db.models import Min
from telegram import user as t_user


class User(models.Model):
    user_id = models.IntegerField(unique=True)
    user_name = models.TextField(null=True)
    first_name = models.TextField(null=True)
    add_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create(cls, user: t_user.User):
        return User.objects.get_or_create(
            user_id=user.id, user_name=user.username, first_name=user.first_name
        )

    def __str__(self):
        return f"{self.pk} - {self.user_id} - {self.user_name}"

    class Meta:
        db_table = "users"

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Langs(models.TextChoices):
    SUB = "SUB", "sub"
    RUS = "RUS", "russian"
    ENG = "ENG", "english"


class Episode(models.Model):

    series = models.ForeignKey("Series", on_delete=models.CASCADE)

    file_id = models.TextField(unique=False)
    message_id = models.IntegerField(unique=True)

    episode = models.IntegerField()
    season = models.IntegerField()
    lang = models.CharField(max_length=3, choices=Langs.choices, default=Langs.RUS)

    def get_season(self):
        return Season(self.series.pk, self.season, self.lang)

    def get_next(self):
        next_episodes = Episode.objects.filter(
            series=self.series,
            season=self.season,
            episode__gt=self.episode,
            lang=self.lang,
        )

        if not len(next_episodes):
            next_episodes = Episode.objects.filter(
                series=self.series,
                season=self.season + 1,
                lang=self.lang,
            )

        next_episode = next_episodes.first()

        try:
            caption = f"{next_episode.episode} >>"
        except AttributeError:
            caption = None

        return next_episode, caption

    def get_previous(self):
        previouses = Episode.objects.filter(
            series=self.series,
            season=self.season,
            episode__lt=self.episode,
            lang=self.lang,
        )

        if not len(previouses):
            previouses = Episode.objects.filter(
                series=self.series,
                season=self.season - 1,
                lang=self.lang,
            )

        previous_episode: Episode = previouses.last()

        try:
            caption = f"<< {previous_episode.episode}"
        except AttributeError:
            caption = None

        return previous_episode, caption

    class Meta:
        unique_together = ["series", "episode", "season", "lang"]
        db_table = "episodes"

        verbose_name = "Эпизоды"
        verbose_name_plural = "Эпизоды"

    def __str__(self):
        return f"{self.series.title} {self.season}/{self.episode} {self.lang}"


class Season:
    def __init__(self, series_pk: int, season: int, lang: str):
        self.series = series_pk
        self.id = season
        self.lang = lang


class Series(models.Model):
    title_ru = models.TextField(unique=True, null=True)
    title_eng = models.TextField(unique=True)
    poster = models.TextField(unique=False, null=True, blank=True)
    genre = models.ManyToManyField("Genre", blank=True)
    desc = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "series"
        verbose_name = "Сериалы"
        verbose_name_plural = "Сериалы"

    @property
    def title(self):
        return f"{self.title_ru} / {self.title_eng}"

    def get_count(self, lang=Langs.RUS) -> int:
        return Episode.objects.filter(series=self, lang=lang).count()

    def get_seasons(self):
        qs = (
            Episode.objects.filter(series=self)
            .values("season", "lang")
            .annotate(mn=Min("pk"))
        )
        return [
            Season(self.pk, episode.get("season"), episode.get("lang"))
            for episode in qs
        ]

    def __str__(self):
        return f"{self.title}"


class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "genres"
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Movie(models.Model):
    title_ru = models.CharField(max_length=56, null=True, blank=True)
    title_eng = models.CharField(max_length=56)

    file_id = models.TextField(unique=False)
    message_id = models.IntegerField(unique=True)
    lang = models.CharField(max_length=3, choices=Langs.choices, default=Langs.RUS)

    poster = models.CharField(max_length=128, null=True, blank=True)
    genre = models.ManyToManyField("Genre", blank=True)
    desc = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "movies"
        verbose_name = "Фильмы"
        verbose_name_plural = "Фильмы"
        unique_together = ["title_ru", "title_eng", "lang"]

    @property
    def title(self):
        return f"{self.title_ru} / {self.title_eng}"

    def __str__(self) -> str:
        return f"{self.title} {self.lang}"
