from django.contrib import admin

from . import models


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    exclude = ("file_id", "message_id")


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    ordering = ("pk",)
    exclude = ("poster",)
    filter_horizontal = ("genre",)


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    pass
