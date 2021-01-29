from django.test import TestCase

from netflix_bot.common import decodeb64, safe_encode


class TestSafeEncode(TestCase):
    def test_success(self):
        text = "пацаны которые че то там"
        a, b = safe_encode(text)
        self.assertIsInstance(a, str)
        self.assertFalse(a.startswith("b"))
        self.assertTrue(len(a) <= 28, f"{len(a)} - {a}")
        self.assertTrue(text.startswith(b), b)
        self.assertEqual(decodeb64(a), b)
