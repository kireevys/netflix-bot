# Create your models here.

from django.db import models


class User(models.Model):
    user_id = models.IntegerField(unique=True)
    chat_id = models.IntegerField(unique=True)
    add_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Video(models.Model):
    series = "series"
    movie = "movie"

    class VideoType(models.TextChoices):
        SERIES = "SER", "series"
        MOVIE = "MOV", "movie"

    video_type = models.CharField(choices=VideoType.choices, max_length=3)

    title = models.TextField()
    duration = models.TimeField(null=True)
    country = models.TextField(null=True)
    release = models.DateField(null=True)
    description = models.TextField(null=True)
    genres = models.TextField(null=True)

    mpa_rating = models.TextField(null=True)
    imdb_rating = models.TextField(null=True)

    add_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "videos"

    @staticmethod
    def add(file_id, message_id, title, season, episode, lang="RU") -> "Series":
        video = Video.objects.create(title=title, video_type=Video.VideoType.SERIES)
        series = Series.objects.create(
            video=video,
            file_id=file_id,
            message_id=message_id,
            season=season,
            episode=episode,
            lang=lang,
        )
        return series

    def __str__(self):
        return self.title


class Series(models.Model):
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    file_id = models.TextField(unique=True)
    message_id = models.IntegerField(null=False)

    episode = models.IntegerField()
    season = models.IntegerField()
    lang = models.CharField(max_length=3)

    def __str__(self):
        return (
            f"{self.video.title}\n"
            f"{self.season:<4} сезон | {self.episode} серия\n"
            f"{self.lang}"
        )


# class Movie(models.Model):
#     video = models.ForeignKey("Video", on_delete=models.CASCADE)
#     file_id = models.TextField(unique=True)
#     franchise = models.TextField(null=True)
#     movie_no = models.IntegerField(null=True)
#
#     class Meta:
#         db_table = "movies"
