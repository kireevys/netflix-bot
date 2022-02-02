from django.db import models  # noqa


class DjangoMessage(models.Model):
    text = models.TextField()
    media_link = models.URLField()
    buttons = models.ManyToManyField("DjangoButton")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message"


class DjangoButton(models.Model):
    text = models.CharField(max_length=64)
    link = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "button"
