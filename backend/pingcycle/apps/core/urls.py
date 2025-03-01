from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import KeywordsViewSet, ChatsViewSet, ping


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register("keywords", KeywordsViewSet, basename="keywords")
router.register("chats", ChatsViewSet, basename="chats")

urlpatterns = [
    path("ping/", ping, name="ping"),
    path("", include(router.urls)),
]
