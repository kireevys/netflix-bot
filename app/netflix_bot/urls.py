from django.urls import path

from .views import UserFileView

urlpatterns = [
    path("users/", UserFileView.as_view()),
]
