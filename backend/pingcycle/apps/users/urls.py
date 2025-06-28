from django.urls import path, include
from .views import delete_account

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("delete-account/", delete_account),
]
