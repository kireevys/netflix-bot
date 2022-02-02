from bulkmail.forms import BulkmailForm
from bulkmail.models import Bulkmail, Button, Message
from bulkmail.senders import BulkmailSender
from bulkmail.serializers import ButtonSerializer, MessageSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from netflix_bot.models import User
from project import settings
from rest_framework import permissions, viewsets
from telegram import Bot


class LoginRequiredView(LoginRequiredMixin, View):
    login_url = "/admin/login/"
    redirect_field_name = "redirect_to"

    def get(self, request: WSGIRequest):
        ...

    def post(self, request: WSGIRequest):
        ...


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ButtonViewSet(viewsets.ModelViewSet):
    queryset = Button.objects.all()
    serializer_class = ButtonSerializer
    permission_classes = [permissions.IsAuthenticated]


class BulkmailView(LoginRequiredView):
    def get(self, request: WSGIRequest):
        return render(request, "bulkmail.html")


class BulkmailCreateView(LoginRequiredView):
    def get(self, request: WSGIRequest):
        return render(request, "bulkmail_create.html", {"form": BulkmailForm()})

    def _build_button(self, btn):
        return btn

    def post(self, request: WSGIRequest, *args):
        _ = request.POST.get("buttons", [])
        form = BulkmailForm(request.POST)

        # Check if the form is valid:
        if not form.is_valid():
            return HttpResponse("404")

        message = Message.objects.create(
            text=form.cleaned_data["text"],
            content=form.cleaned_data["content"],
            buttons=form.cleaned_data["buttons"],
        )
        bulkmail = Bulkmail.objects.create(message=message)
        bulkmail.add_users(User.objects.filter(user_id=362954912))
        BulkmailSender(Bot(settings.BOT_TOKEN)).run(bulkmail)
        return redirect("/bulkmail/")
