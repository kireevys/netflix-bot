from django.urls import re_path

from .views import CommandReceiveView

urlpatterns = [
    re_path(r'bot/', CommandReceiveView.as_view()),
]
