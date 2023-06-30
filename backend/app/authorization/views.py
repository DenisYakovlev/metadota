from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class SignIn(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                       context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth_token': token.key,
            'gsi_token': user.gsi_token
        }, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def SignUp(request):
    serializer = RegistrationSerializer(data=request.data)
        
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get_or_create(user=user)
        
        data = {
            "auth_token": Token.objects.get(user=user).key,
            "gsi_token": user.gsi_token
        }
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)