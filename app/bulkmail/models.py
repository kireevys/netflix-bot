from django.db import models

from bulkmail.message import Message
from netflix_bot.models import User


class Status(models.TextChoices):
    SENDED = "S", "sended"
    NEW = "N", "new"


class Bulkmail(models.Model):
    message = models.JSONField()
    status = models.CharField(choices=Status.choices, max_length=16, default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)
    sended = models.DateTimeField(null=True)

    @classmethod
    def create(cls, message: Message) -> "Bulkmail":
        return cls.objects.create(message=message)


class Recipients(models.Model):
    bulkmail = models.ForeignKey(Bulkmail, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
