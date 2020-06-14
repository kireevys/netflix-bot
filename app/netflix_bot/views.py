# Create your views here.
# import json
import logging

# from django.conf import settings
from django.http import (
    # HttpResponseForbidden,
    JsonResponse,
)
# from django.utils.decorators import method_decorator
from django.views import View

# from django.views.decorators.csrf import csrf_exempt
# from telegram import Update

logger = logging.getLogger(__name__)


# if settings.DEBUG:
#     from netflix_bot.telegram_bot.main import up_bot
#
#     disp = up_bot()


class CommandReceiveView(View):
    def get(self, request):
        return JsonResponse({}, status=403)

    # def post(self, request, bot_token):
    #     logger.info(request)
    #     logger.info(bot_token)
    #     if bot_token != settings.BOT_TOKEN:
    #         logger.error('HAS NOT BOT TOKEN')
    #         return HttpResponseForbidden("Invalid token")
    #
    #     raw = request.body.decode("utf-8")
    #     logger.info(raw)
    #     update: Update = Update.de_json(json.loads(raw), bot.bot)
    #     logger.info(update)
    #     bot.process_update(update)
    #
    #     return JsonResponse({}, status=200)
    #
    # @method_decorator(csrf_exempt)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
