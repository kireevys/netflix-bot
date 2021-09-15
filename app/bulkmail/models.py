from functools import cached_property
from typing import TypedDict

from django.db import models
from django.db.models import QuerySet
from netflix_bot.models import User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Button(TypedDict):
    text: str
    link: str


class Message(models.Model):
    class ContentTypes(models.TextChoices):
        PHOTO = "PHOTO"
        ANIMATION = "ANIMA"
        VIDEO = "VIDEO"
        EMPTY = "EMPTY"

    text = models.TextField()
    buttons = models.JSONField()
    content = models.URLField()
    content_type = models.CharField(
        max_length=5,
        choices=ContentTypes.choices,
        default=ContentTypes.EMPTY,
    )
    created = models.DateTimeField(auto_now_add=True)

    @cached_property
    def get_keyboard(self):
        keyboard = InlineKeyboardMarkup([])

        for button in self.buttons:  # type: Button
            btn = InlineKeyboardButton(text=button.get("text"), url=button.get("link"))
            keyboard.inline_keyboard.append([btn])

        return keyboard


class Bulkmail(models.Model):
    class Statuses(models.TextChoices):
        NEW = "NEW"
        PROGRESS = "PRG"
        ERROR = "ERR"
        SUCCESS = "SUC"

    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=5,
        choices=Statuses.choices,
        default=Statuses.NEW,
    )
    duration = models.TimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def add_users(self, users: QuerySet[User]):
        for_send = [SendList(title=self, user=user) for user in users]
        SendList.objects.bulk_create(for_send)

    def get_list(self) -> QuerySet["SendList"]:
        return SendList.objects.filter(title=self)


class SendList(models.Model):
    class Statuses(models.TextChoices):
        NEW = "NEW"
        ERROR = "ERR"
        SUCCESS = "SUC"

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.ForeignKey(Bulkmail, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    sended = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=5,
        choices=Statuses.choices,
        default=Statuses.NEW,
    )
