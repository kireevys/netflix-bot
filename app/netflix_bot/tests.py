from django.test import TestCase

from netflix_bot import models
from .telegram_bot.managers import SeriesManager


class TestSeriesManager(TestCase):
    def test_language_correct_choice(self):
        for title, season, episode, lang, expect in [
            ("test", 1, 1, "ENG", "ENG"),
            ("test", 1, 1, "Eng", "ENG"),
            ("test", 1, 1, "eng", "ENG"),
            ("test", 1, 1, "RUS", "RUS"),
            ("test", 1, 1, "Rus", "RUS"),
            ("test", 1, 1, "ruS", "RUS"),
            ("test", 1, 1, "SUB", "SUB"),
            ("test", 1, 1, "Озвучка bla bla", "RUS"),
            ("test", 1, 1, "Озвучка", "RUS"),
        ]:
            with self.subTest(lang):
                manager = SeriesManager(title, season, episode, lang)
                self.assertEqual(manager.lang, expect)

    def test_caption_parser(self):
        for caption, title, season, episode, lang in [
            ("Тест/Test\n1 сезон/1 серия", "Тест/Test", 1, 1, models.Episode.Langs.RUS),
            (
                "Тест/Test\n1 сезон/1 серия\nRUS",
                "Тест/Test",
                1,
                1,
                models.Episode.Langs.RUS,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nENG",
                "Тест/Test",
                1,
                1,
                models.Episode.Langs.ENG,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nEnG",
                "Тест/Test",
                1,
                1,
                models.Episode.Langs.ENG,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nОзвучка",
                "Тест/Test",
                1,
                1,
                models.Episode.Langs.RUS,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nSUB",
                "Тест/Test",
                1,
                1,
                models.Episode.Langs.SUB,
            ),
            (
                "Тест/Test\n1 сезон/2 серия\nSUB",
                "Тест/Test",
                1,
                2,
                models.Episode.Langs.SUB,
            ),
            (
                "Тест / Test\n123 сезон/2123 серия\nSUB",
                "Тест / Test",
                123,
                2123,
                models.Episode.Langs.SUB,
            ),
            (
                "Тест/Test\n123 s / 2123 серия\nSUB",
                "Тест/Test",
                123,
                2123,
                models.Episode.Langs.SUB,
            ),
            (
                "Тест/Test\n123 season / 2123 episode",
                "Тест/Test",
                123,
                2123,
                models.Episode.Langs.RUS,
            ),
        ]:
            with self.subTest(caption):
                manager = SeriesManager.from_caption(caption)
                self.assertEqual(manager.title, title)
                self.assertEqual(manager.season, season)
                self.assertEqual(manager.episode, episode)
                self.assertEqual(manager.lang, lang)
