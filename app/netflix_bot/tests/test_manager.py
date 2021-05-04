from django.test import TransactionTestCase

from netflix_bot import models
from netflix_bot.models import Series
from series.loader import SeriesManager


class TestSeriesManager(TransactionTestCase):
    def setUp(self) -> None:
        self.captions_input = [
            (
                "Тест/Test\n1 сезон/1 серия",
                "Тест / Test",
                1,
                1,
                models.Langs.RUS,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nRUS",
                "Тест / Test",
                1,
                1,
                models.Langs.RUS,
            ),
            (
                "   Тест /Test\n1 сезон/1 серия\nENG",
                "Тест / Test",
                1,
                1,
                models.Langs.ENG,
            ),
            (
                "Тест/ Test\n1 сезон/1 серия\nEnG",
                "Тест / Test",
                1,
                1,
                models.Langs.ENG,
            ),
            (
                " Тест/Test \n1 сезон/1 серия\nОзвучка",
                "Тест / Test",
                1,
                1,
                models.Langs.RUS,
            ),
            (
                "Тест/Test\n1 сезон/1 серия\nSUB",
                "Тест / Test",
                1,
                1,
                models.Langs.SUB,
            ),
            (
                "Тест / Test\n1 сезон/2 серия\nSUB",
                "Тест / Test",
                1,
                2,
                models.Langs.SUB,
            ),
            (
                "Тест / Test\n123 сезон/2123 серия\nSUB",
                "Тест / Test",
                123,
                2123,
                models.Langs.SUB,
            ),
            (
                "Тест / Test\n123 s / 2123 серия\nSUB",
                "Тест / Test",
                123,
                2123,
                models.Langs.SUB,
            ),
            (
                "Тест / Test\n123 season / 2123 episode",
                "Тест / Test",
                123,
                2123,
                models.Langs.RUS,
            ),
        ]

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
                manager = SeriesManager(title, title, lang, season, episode)
                self.assertEqual(manager.lang, expect)

    def test_parse_caption(self):
        for caption, title, season, episode, lang in self.captions_input:
            with self.subTest(caption):
                title_ru, title_eng = title.split("/")

                manager = SeriesManager.from_caption(caption)
                self.assertEqual(manager.title_ru, title_ru.strip())
                self.assertEqual(manager.title_eng, title_eng.strip())
                self.assertEqual(manager.title, title)
                self.assertEqual(manager.season, season)
                self.assertEqual(manager.episode, episode)
                self.assertEqual(manager.lang, lang)

    def test_write_episode_after_parse_caption(self):
        for caption, title, season, episode, lang in self.captions_input:
            with self.subTest(caption):
                title_ru, title_eng = title.split("/")

                manager = SeriesManager.from_caption(caption)
                parsed_episode = manager.write("test_id", 123)

                series = Series.objects.get(id=parsed_episode.series.id)

                self.assertEqual(series.title_ru, title_ru.strip())
                self.assertEqual(series.title_eng, title_eng.strip())
                self.assertEqual(series.title, title)

                self.assertEqual(parsed_episode.episode, episode)
                self.assertEqual(parsed_episode.lang, lang)
                self.assertEqual(parsed_episode.season, season)

                # tearDown
                parsed_episode.delete()
                series.delete()
