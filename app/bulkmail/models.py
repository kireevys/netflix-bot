from django.db import models  # noqa


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
        return f"{self.text}"


class DjangoRecipient(models.Model):
    user = models.ForeignKey("netflix_bot.User", on_delete=models.SET_NULL, null=True)
    address = models.IntegerField()


class UserTag(models.Model):
    class Tags(models.TextChoices):
        TEST = "TEST", "test user"
        ANY = "ANY", "Any user"

    user = models.ForeignKey("netflix_bot.User", on_delete=models.CASCADE)
    tag = models.CharField(max_length=5, choices=Tags.choices, default=Tags.ANY)
