# Generated by Django 3.0.6 on 2020-08-09 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netflix_bot", "0002_username_nullable"),
    ]

    operations = [
        migrations.AddField(
            model_name="series",
            name="poster",
            field=models.TextField(null=True),
        ),
    ]
