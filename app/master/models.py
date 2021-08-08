# Create your models here.
from django.db import models


class Slave(models.Model):
    name = models.CharField(max_length=126)
    series = models.IntegerField()
    movies = models.IntegerField()
    enabled = models.BooleanField(default=True)
    created = models.DateTimeField(auto_created=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.enabled}"
