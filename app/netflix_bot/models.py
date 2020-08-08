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


class Episode(models.Model):
    class Langs(models.TextChoices):
        SUB = "SUB", "sub"
        RUS = "RUS", "russian"
        ENG = "ENG", "english"

    series = models.ForeignKey("Series", on_delete=models.CASCADE)

    file_id = models.TextField(unique=False)
    message_id = models.IntegerField(unique=True)

    episode = models.IntegerField()
    season = models.IntegerField()
    lang = models.CharField(max_length=3, choices=Langs.choices, default=Langs.RUS)

    def get_next(self):
        next_episode = Episode.objects.filter(series=self.series, season=self.season, episode__gt=self.episode)

        if not len(next_episode):
            try:
                next_episode = Episode.objects.get(series=self.series, season=self.season + 1, episode=1)
                return next_episode
            except Episode.DoesNotExist:
                return None

        return next_episode.first()

    def get_previous(self):
        previous = Episode.objects.filter(series=self.series, season=self.season, episode__lt=self.episode)

        if not len(previous):
            try:
                previous = Episode.objects.filter(series=self.series, season=self.season - 1)
            except Episode.DoesNotExist:
                return None

        return previous.last()

    class Meta:
        unique_together = ["series", "episode", "season", "lang"]
        db_table = "episodes"

    def __str__(self):
        return f"{self.series.title} {self.season}/{self.episode} {self.lang}"


class Season:
    def __init__(self, series_pk: int, season: int, lang: str):
        self.series = series_pk
        self.id = season
        self.lang = lang


class Series(models.Model):
    title = models.TextField(unique=True)
    desc = models.TextField(null=True)

    class Meta:
        db_table = "series"

    def get_count(self, lang=Episode.Langs.RUS) -> int:
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
        return f"{self.pk} {self.title}"
