import json

from django.test import TestCase

from bulkmail.models import (
    Bulkmail,
)


class TestBulkmail(TestCase):
    """Проверка массовых рассылок."""

    def test_create_bulkmail(self):
        """Проверка создания массовой рассылки."""
        media = "http://media.png"
        text = "Some Text"
        buttons = [Button(title="Button", url="t.me/url")]
        message = Message(media=media, text=text, buttons=buttons)
        bulkmail = Bulkmail.create(message)

        self.assertDictEqual(
            bulkmail.message,
            {
                "media": media,
                "text": text,
                "buttons": [
                    {"title": "Button", "url": "t.me/url"},
                ],
            },
        )
