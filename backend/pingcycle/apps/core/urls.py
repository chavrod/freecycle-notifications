from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import UserSelectedKeywordsViewSet, ping


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    "products", UserSelectedKeywordsViewSet, basename="user-selected-keywords"
)

urlpatterns = [
    path("ping/", ping, name="ping"),
    path("", include(router.urls)),
]
