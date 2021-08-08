from django.contrib import admin
from master import models


@admin.register(models.Slave)
class EpisodeAdmin(admin.ModelAdmin):
    ...
