from bulkmail import models
from django.contrib import admin


@admin.register(models.DjangoMessage)
class DjangoMessageAdmin(admin.ModelAdmin):
    ordering = ("-created", "-updated")
    filter_horizontal = ("buttons",)


@admin.register(models.DjangoButton)
class DjangoButtonAdmin(admin.ModelAdmin):
    ordering = ("-created", "-updated")
