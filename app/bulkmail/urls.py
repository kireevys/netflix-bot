from django.urls import re_path

from .views import BulkmailView

urlpatterns = [
    re_path(r"bulkmail", BulkmailView.as_view()),
]
