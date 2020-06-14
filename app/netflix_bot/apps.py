from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = "netflix_bot"

    def ready(self):
        from netflix_bot.telegram_bot.main import up_bot
        up_bot()
