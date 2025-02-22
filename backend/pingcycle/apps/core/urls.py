from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import KeywordsViewSet, ping


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register("keywords", KeywordsViewSet, basename="keywords")

urlpatterns = [
    path("ping/", ping, name="ping"),
    path("", include(router.urls)),
]
