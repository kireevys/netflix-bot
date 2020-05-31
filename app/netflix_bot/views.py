# Create your views here.
import logging

from django.conf import settings
from django.http import (
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


class CommandReceiveView(View):
    def post(self, request, bot_token):
        if bot_token != settings.BOT_TOKEN:
            return HttpResponseForbidden("Invalid token")

        raw = request.body.decode("utf-8")
        logger.info(raw)

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
