from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from bulkmail.forms import BulkmailForm
from bulkmail.message import Message
from bulkmail.sender import TelegramSender
from bulkmail.sender import Builkmail
from netflix_bot import models


class BulkmailView(View):
    def get(self, request):
        form = BulkmailForm()
        return render(request, "bulkmail.html", {"form": form})

    def post(self, request):
        form = BulkmailForm(request.POST)

        if form.is_valid():
            _, text, media = form.cleaned_data.values()
            message = Message(text, [], media)
            sender = TelegramSender()
            users = models.User.objects.filter(authorize=True)
            Builkmail().bulk(message, users, sender)
            return HttpResponse("Sended!")
