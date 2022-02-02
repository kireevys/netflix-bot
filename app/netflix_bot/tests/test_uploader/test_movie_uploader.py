from unittest.mock import MagicMock, patch

from django.test import TestCase
from netflix_bot.models import Langs, Movie
from netflix_bot.telegram_bot.uploaders import MovieUploader


class TestSeriesUploader(TestCase):
    uploaders_path = "netflix_bot.telegram_bot.uploaders"

    def setUp(self) -> None:
        self.title_ru = "Test"
        self.title_eng = "Test"

        self.movie_ru = Movie.objects.create(
            title_ru=self.title_ru,
            title_eng=self.title_eng,
            lang=Langs.RUS,
            message_id=1,
        )
        self.movie_eng = Movie.objects.create(
            title_ru=self.title_ru,
            title_eng=self.title_eng,
            lang=Langs.ENG,
            message_id=2,
        )
        self.movie_sub = Movie.objects.create(
            title_ru=self.title_ru,
            title_eng=self.title_eng,
            lang=Langs.SUB,
            message_id=3,
        )

        self.update = MagicMock(
            effective_message=MagicMock(reply_to_message=MagicMock(message_id=1))
        )
        self.context = MagicMock()

    def test_add_multiple_poster(self):
        self.update.channel_post.caption = f"{self.title_ru}/{self.title_eng}"

        with patch(
            f"{self.uploaders_path}.Uploader.is_upload_channel",
            return_value=True,
        ):
            uploader = MovieUploader(self.update, self.context)

            file_id = "file_id"
            uploader.add_poster(file_id)

        self.movie_ru.refresh_from_db()
        self.assertEqual(
            self.movie_ru.poster, file_id, "not added poster to default lang"
        )

        self.movie_sub.refresh_from_db()
        self.assertEqual(
            self.movie_sub.poster, file_id, "not added poster to another lang"
        )

        self.movie_eng.refresh_from_db()
        self.assertEqual(
            self.movie_sub.poster, file_id, "not added poster to another lang"
        )

    def test_add_poster_to_not_exists_series(self):
        self.update.channel_post.caption = f"not exists/{self.title_eng}\nENG"
        self.update.effective_message.reply_to_message.message_id = (
            self.movie_ru.message_id
        )

        with patch(
            f"{self.uploaders_path}.Uploader.is_upload_channel",
            return_value=True,
        ):
            uploader = MovieUploader(self.update, self.context)

        file_id = "some"
        with self.assertRaises(Movie.DoesNotExist):
            uploader.add_poster(file_id)

    def test_add_description(self):
        caption = f"{self.title_ru}/{self.title_eng} | some"
        expected = "some"

        self.update = MagicMock(
            effective_message=MagicMock(reply_to_message=MagicMock(message_id=1))
        )

        with patch(
            f"{self.uploaders_path}.Uploader.is_upload_channel",
            return_value=True,
        ):
            uploader = MovieUploader(self.update, self.context)

        uploader.add_description(caption)

        self.movie_ru.refresh_from_db()
        self.assertEqual(self.movie_ru.desc, expected)

        self.movie_eng.refresh_from_db()
        self.assertEqual(self.movie_eng.desc, expected)

        self.movie_sub.refresh_from_db()
        self.assertEqual(self.movie_sub.desc, expected)

    def test_add_description_to_not_exists_movie(self):
        self.update = MagicMock(
            effective_message=MagicMock(reply_to_message=MagicMock(message_id=5))
        )

        with patch(
            f"{self.uploaders_path}.Uploader.is_upload_channel",
            return_value=True,
        ):
            uploader = MovieUploader(self.update, self.context)

        with self.assertRaises(ValueError):
            uploader.add_description(f"not exists/{self.title_eng} | ENG")
