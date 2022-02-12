from bulkmail import models
from django.contrib import admin


class ButtonInline(admin.StackedInline):
    model = models.DjangoButton


@admin.register(models.DjangoMessage)
class MessageAdmin(admin.ModelAdmin):
    model = models.DjangoMessage

    inlines = [
        ButtonInline,
    ]


@admin.register(models.DjangoBulkmail)
class BulkmailAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Envelope)
class EnvelopeAdmin(admin.ModelAdmin):
    ordering = ["status"]
