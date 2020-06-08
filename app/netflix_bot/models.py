# Create your models here.

from django.db import models
from django.db.models import Min


class User(models.Model):
    user_id = models.IntegerField(unique=True)
    chat_id = models.IntegerField(unique=True)
    add_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Episode(models.Model):
    class Langs(models.TextChoices):
        SUB = "SUB", "sub"
        RUS = "RUS", "russian"
        ENG = "ENG", "english"

    series = models.ForeignKey("Series", on_delete=models.CASCADE)

    file_id = models.TextField(unique=True)
    message_id = models.IntegerField(unique=True)

    episode = models.IntegerField()
    season = models.IntegerField()
    lang = models.CharField(max_length=3, choices=Langs.choices, default=Langs.RUS)

    class Meta:
        unique_together = ["series", "episode", "season", "lang"]
        db_table = "episodes"

    def __str__(self):
        return f"{self.series.title} {self.season}/{self.episode} {self.lang}"


class Series(models.Model):

    title = models.TextField(unique=True)
    desc = models.TextField(null=True)

    class Meta:
        db_table = "series"

    def get_count(self, lang=Episode.Langs.RUS) -> int:
        return Episode.objects.filter(series=self, lang=lang).count()

    def get_seasons(self):
        return (
            Episode.objects.filter(series=self)
            .values("season", "lang")
            .annotate(mn=Min("pk"))
        )

    def __str__(self):
        return f"{self.pk} {self.title}"
