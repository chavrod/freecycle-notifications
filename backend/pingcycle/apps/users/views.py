from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

    if user.is_authenticated:
        user.delete()
        return Response({"message": "Account deleted successfully."})
    else:
        return Response({"error": "Unauthorized user."}, status=401)
