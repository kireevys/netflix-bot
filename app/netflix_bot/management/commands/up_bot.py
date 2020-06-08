from django.core.management.base import BaseCommand

from netflix_bot.core.main import up_bot


class Command(BaseCommand):
    help = "Bot up"

    def handle(self, *args, **options):
        up_bot()
