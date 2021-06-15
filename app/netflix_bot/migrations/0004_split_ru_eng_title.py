# Generated by Django 3.1 on 2020-08-23 09:42

from django.db import migrations, models


def split_title(apps, schema_editor):
    Series = apps.get_model("netflix_bot", "Series")
    all_series = Series.objects.all()

    for series in all_series:
        title_ru, title_eng = series.title_eng.split("/")

        series.title_ru = title_ru.strip()
        series.title_eng = title_eng.strip()
        series.save()


class Migration(migrations.Migration):
    dependencies = [
        ("netflix_bot", "0003_add_poster"),
    ]

    operations = [
        migrations.RenameField(
            model_name="series",
            old_name="title",
            new_name="title_eng",
        ),
        migrations.AddField(
            model_name="series",
            name="title_ru",
            field=models.TextField(null=True, unique=True),
        ),
        migrations.RunPython(split_title),
    ]
