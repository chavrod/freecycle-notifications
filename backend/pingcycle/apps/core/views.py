from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import JsonResponse

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Keyword
from .serializers import KeywordsSerializer, KeywordsCreationSerializer


@csrf_protect
def ping(request):
    csrf_token = get_token(request)
    response = JsonResponse({"status": "OK", "csrfToken": csrf_token})
    response.set_cookie("csrftoken", csrf_token)
    return response


class KeywordsViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_keywords = Keyword.objects.filter(user=request.user)
        serializer = KeywordsSerializer(user_keywords, many=True)
        print(" serializer.data", serializer.data)
        return Response({"keywords": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = KeywordsCreationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            Keyword.objects.create(
                name=serializer.validated_data["name"], user=request.user
            )
            return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            keyword = Keyword.objects.get(pk=pk, user=request.user)
            keyword.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Keyword.DoesNotExist:
            return Response(
                {"error": "Keyword not found."}, status=status.HTTP_404_NOT_FOUND
            )
