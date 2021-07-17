from unittest.mock import MagicMock, patch

from django.test import TestCase
from netflix_bot.models import Episode, Series
from netflix_bot.telegram_bot.uploaders import SeriesUploader


class TestUploader(TestCase):
    uploaders_path = "netflix_bot.telegram_bot.uploaders"

    def setUp(self) -> None:
        self.title_ru = "Тест"
        self.title_eng = "Test"

        self.update = MagicMock()
        self.context = MagicMock()

    def test_check_allowed_chat_id(self):
        self.update.channel_post.caption = (
            f"{self.title_ru}/{self.title_eng}\n1 сезон/1 серия\nENG"
        )

        for is_it in True, False:
            with patch(
                f"{self.uploaders_path}.SeriesUploader.is_upload_channel",
                return_value=is_it,
            ):
                if not is_it:
                    with self.assertRaises(ConnectionAbortedError):
                        SeriesUploader(self.update, self.context)
                else:
                    SeriesUploader(self.update, self.context)


class TestSeriesUploader(TestCase):
    uploaders_path = "netflix_bot.telegram_bot.uploaders"

    def setUp(self) -> None:
        self.title_ru = "Test"
        self.title_eng = "Test"

        self.series = Series.objects.create(
            title_ru=self.title_ru, title_eng=self.title_eng
        )
        self.episode = Episode.objects.create(
            series=self.series, message_id=1, file_id="some", episode=1, season=1
        )

        self.update = MagicMock(
            effective_message=MagicMock(
                reply_to_message=MagicMock(message_id=1))
        )
        self.context = MagicMock()

    def test_add_poster(self):
        self.update.channel_post.caption = (
            f"{self.title_ru}/{self.title_eng}\n1 сезон/1 серия\nENG"
        )

        with patch(
            f"{self.uploaders_path}.SeriesUploader.is_upload_channel",
            return_value=True,
        ):
            uploader = SeriesUploader(self.update, self.context)

        file_id = "file_id"
        uploader.add_poster(file_id)

        self.series.refresh_from_db()
        self.assertEqual(self.series.poster, file_id)

    def test_add_poster_to_not_exists_series(self):
        self.update.channel_post.caption = (
            f"not exists/{self.title_eng}\n1 сезон/1 серия\nENG"
        )
        self.update.effective_message.reply_to_message.message_id = (
            self.episode.message_id
        )

        with patch(
            f"{self.uploaders_path}.SeriesUploader.is_upload_channel",
            return_value=True,
        ):
            uploader = SeriesUploader(self.update, self.context)

        file_id = "some"
        with self.assertRaises(Series.DoesNotExist):
            uploader.add_poster(file_id)

    def test_add_description(self):
        self.update.channel_post.caption = (
            f"not exists/{self.title_eng}\n1 сезон/1 серия\nENG"
        )

        self.update = MagicMock(
            effective_message=MagicMock(
                reply_to_message=MagicMock(message_id=1))
        )

        with patch(
            f"{self.uploaders_path}.SeriesUploader.is_upload_channel",
            return_value=True,
        ):
            uploader = SeriesUploader(self.update, self.context)

        desc = "some"
        uploader.add_description(desc)

        self.series.refresh_from_db()
        self.assertEqual(self.series.desc, desc)

    def test_add_description_to_not_exists_series(self):
        self.update.channel_post.caption = (
            f"not exists/{self.title_eng}\n1 сезон/1 серия\nENG"
        )

        self.update = MagicMock(
            effective_message=MagicMock(
                reply_to_message=MagicMock(message_id=2))
        )

        with patch(
            f"{self.uploaders_path}.SeriesUploader.is_upload_channel",
            return_value=True,
        ):
            uploader = SeriesUploader(self.update, self.context)

        desc = "some"
        with self.assertRaises(Series.DoesNotExist):
            uploader.add_description(desc)
