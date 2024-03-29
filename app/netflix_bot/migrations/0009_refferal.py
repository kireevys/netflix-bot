# Generated by Django 3.1 on 2021-02-11 09:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netflix_bot", "0008_fill_ru_title_upper"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movie",
            name="title_ru_upper",
            field=models.TextField(max_length=56),
        ),
        migrations.AlterField(
            model_name="series",
            name="title_ru_upper",
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name="Referral",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("owner", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "refferal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="netflix_bot.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Реферал",
                "verbose_name_plural": "Рефералы",
                "db_table": "referrals",
                "unique_together": {("owner", "refferal")},
            },
        ),
    ]
