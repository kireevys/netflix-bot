import logging

from django.conf import settings

from netflix_bot import models

logger = logging.getLogger()


class VideoManager:
    def __init__(self, title_ru, title_eng, lang, **kwargs):
        self.title_ru = title_ru
        self.title_eng = title_eng
        self.lang = self.get_lang(lang.upper())

    @staticmethod
    def _strip_ok_emoji(caption: str) -> str:
        if caption.startswith(settings.EMOJI.get("ok")):
            caption = caption.strip(settings.EMOJI.get("ok"))

        return caption

    @property
    def title(self):
        return f"{self.title_ru} / {self.title_eng}"

    @staticmethod
    def get_lang(lang: str):
        if lang not in models.Langs:
            logger.info(f"incorrect lang {lang}. Using default")
            return models.Langs.RUS.name

        return lang
