from django.contrib import admin

from . import models


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    exclude = ("file_id", "message_id")
    ordering = ("series", "lang", "season", "episode")


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    ordering = ("id",)
    date_hierarchy = "add_date"


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    ordering = ("pk",)
    exclude = ("poster",)
    filter_horizontal = ("genre",)


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    ordering = ("name",)


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    ordering = ("title_ru",)
    filter_horizontal = ("genre",)


@admin.register(models.Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "view_owner_count",
        "refferal",
        "created_at",
    )
    search_fields = ("owner",)

    def view_owner_count(self, obj: models.Referral):
        return models.Referral.objects.filter(owner=obj.owner).count()
