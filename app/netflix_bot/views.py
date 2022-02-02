import csv
import logging
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.static import serve
from netflix_bot.models import User

logger = logging.getLogger(__name__)


class UserFileView(LoginRequiredMixin, View):
    login_url = "/admin/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        users = User.objects.all().values_list("user_id")
        filename = "users.csv"
        with open(filename, "w", newline="") as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(users)

        return serve(request, os.path.basename(filename), os.path.dirname(filename))
