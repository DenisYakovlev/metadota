from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserList


class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user)

        return Response(status.HTTP_200_OK)