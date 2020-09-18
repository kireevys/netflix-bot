# Generated by Django 3.1 on 2020-09-19 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netflix_bot', '0005_add_genres'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'verbose_name': 'Эпизоды', 'verbose_name_plural': 'Эпизоды'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.AlterModelOptions(
            name='series',
            options={'verbose_name': 'Сериалы', 'verbose_name_plural': 'Сериалы'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterField(
            model_name='series',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='genre',
            field=models.ManyToManyField(blank=True, to='netflix_bot.Genre'),
        ),
        migrations.AlterField(
            model_name='series',
            name='poster',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ru', models.CharField(blank=True, max_length=56, null=True)),
                ('title_eng', models.CharField(max_length=56)),
                ('file_id', models.TextField()),
                ('message_id', models.IntegerField(unique=True)),
                ('lang', models.CharField(choices=[('SUB', 'sub'), ('RUS', 'russian'), ('ENG', 'english')], default='RUS', max_length=3)),
                ('poster', models.CharField(blank=True, max_length=128, null=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('genre', models.ManyToManyField(blank=True, to='netflix_bot.Genre')),
            ],
            options={
                'verbose_name': 'Фильмы',
                'verbose_name_plural': 'Фильмы',
                'db_table': 'movies',
            },
        ),
    ]
