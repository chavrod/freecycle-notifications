from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import JsonResponse

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import UserSelectedKeywords
from .serializers import UserSelectedKeywordsSerializer


@csrf_protect
def ping(request):
    csrf_token = get_token(request)
    response = JsonResponse({"status": "OK", "csrfToken": csrf_token})
    response.set_cookie("csrftoken", csrf_token)
    return response


class UserSelectedKeywordsViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_keywords = UserSelectedKeywords.objects.filter(user=request.user)
        serializer = UserSelectedKeywordsSerializer(user_keywords, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserSelectedKeywordsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            UserSelectedKeywords.objects.create(
                name=serializer.validated_data["name"], user=request.user
            )
            return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            keyword = UserSelectedKeywords.objects.get(pk=pk, user=request.user)
            keyword.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserSelectedKeywords.DoesNotExist:
            return Response(
                {"error": "Keyword not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None, *args, **kwargs):
        try:
            keyword = UserSelectedKeywords.objects.get(pk=pk, user=request.user)
        except UserSelectedKeywords.DoesNotExist:
            return Response(
                {"error": "Keyword not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSelectedKeywordsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            keyword.name = serializer.validated_data["name"]
            keyword.save(update_fields=["name"])
            return Response(status=status.HTTP_200_OK)
