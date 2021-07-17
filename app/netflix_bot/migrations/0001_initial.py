# Generated by Django 3.0.6 on 2020-07-13 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(unique=True)),
                ('desc', models.TextField(null=True)),
            ],
            options={
                'db_table': 'series',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('user_name', models.TextField()),
                ('first_name', models.TextField()),
                ('add_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.TextField(unique=True)),
                ('message_id', models.IntegerField(unique=True)),
                ('episode', models.IntegerField()),
                ('season', models.IntegerField()),
                ('lang',
                 models.CharField(choices=[('SUB', 'sub'), ('RUS', 'russian'), ('ENG', 'english')], default='RUS',
                                  max_length=3)),
                ('series', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='netflix_bot.Series')),
            ],
            options={
                'db_table': 'episodes',
                'unique_together': {('series', 'episode', 'season', 'lang')},
            },
        ),
    ]
