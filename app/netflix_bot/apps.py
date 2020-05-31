from django.apps import AppConfig

from netflix_bot.core.main import run
import sys


class ProjectConfig(AppConfig):
    name = "netflix_bot"

    def ready(self):
        is_unitests = "test" in sys.argv
        if not is_unitests:
            run()
