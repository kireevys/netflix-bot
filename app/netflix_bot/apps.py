import sys

from django.apps import AppConfig

from netflix_bot.core.main import run


class ProjectConfig(AppConfig):
    name = "netflix_bot"

    def ready(self):
        is_unitests = "test" in sys.argv
        if not is_unitests:
            run()
