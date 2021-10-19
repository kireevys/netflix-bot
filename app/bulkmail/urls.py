from django.urls import include, path
from rest_framework import routers

from . import views
from .views import BulkmailCreateView, BulkmailView

router = routers.DefaultRouter()
router.register(r"messages", views.MessageViewSet)
router.register(r"buttons", views.ButtonViewSet)

urlpatterns = [
    path("bulkmail/", BulkmailView.as_view()),
    path("bulkmail/create", BulkmailCreateView.as_view(), name="bulkmail-create"),
    path("", include(router.urls), name="bulkmail"),
]
