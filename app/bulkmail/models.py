from typing import List

from bulkmail.internal.core.bulkmail import BulkmailInfo
from bulkmail.internal.core.message import Button
from django.db import models
from netflix_bot.models import User


class DjangoMessage(models.Model):
    text = models.TextField()
    media_link = models.URLField()
    buttons = models.ManyToManyField("DjangoButton")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message"

        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        crop_len = 15
        ending = ""

        if len(self.text) > crop_len:
            ending = "..."

        return f"{self.text[:crop_len]}{ending} {self.created}"


class DjangoButton(models.Model):
    text = models.CharField(max_length=64)
    link = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "button"

        verbose_name = "Кнопка"
        verbose_name_plural = "Кнопки"

    def __str__(self):
        return self.text


class UserTag(models.Model):
    class Tags(models.TextChoices):
        TEST = "TEST", "test user"
        ANY = "ANY", "Any user"

    user = models.ForeignKey("netflix_bot.User", on_delete=models.CASCADE)
    tag = models.CharField(max_length=5, choices=Tags.choices, default=Tags.ANY)


class DjangoBulkmail(models.Model):
    title = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=128)
    price = models.DecimalField(decimal_places=2, max_digits=9)

    @property
    def bulkmail_info(self) -> BulkmailInfo:
        return BulkmailInfo(
            title=self.title,
            created=self.created,
            customer=self.customer,
            price=float(self.price),
        )


class Envelope(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "NEW"

    bulkmail = models.ForeignKey(DjangoBulkmail, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(max_length=6, choices=Status.choices, default=Status.NEW)
    media = models.URLField()
    keyboard = models.JSONField(default=[])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def buttons(self) -> List[Button]:
        return [Button(**i) for i in self.keyboard]
