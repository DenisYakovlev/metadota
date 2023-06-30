from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response

from .serializers import UserSerializer
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UserInfo(request):
    user = request.user
    serializer = UserSerializer(request.user)
    
    return Response(serializer.data, status=status.HTTP_200_OK)