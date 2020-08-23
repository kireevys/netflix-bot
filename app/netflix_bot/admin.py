from django.contrib import admin

from .models import User, Episode, Series


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    exclude = ('file_id', 'message_id')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    exclude = ('poster', )
