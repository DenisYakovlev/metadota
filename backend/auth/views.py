from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


def clean_cookies(response):
    """
    Just clean token cookies from response object
    """
    response.delete_cookie(settings.AUTH_TOKEN_NAMES['REFRESH_TOKEN_NAME'])
    response.delete_cookie(settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME'])
    response.delete_cookie(settings.AUTH_TOKEN_NAMES['GSI_TOKEN_NAME'])

    return response
    
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Overrided post method from TokenRefreshView
    Added cookie management and also added gsi_token 
    to data of serializer(look for .serializers.GSITokenObtainPairSerializer)
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        response = Response(status.HTTP_200_OK)

        response.set_cookie(
            settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME'],
            value=serializer.validated_data['access'],
            httponly=True,
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        )

        response.set_cookie(
            settings.AUTH_TOKEN_NAMES['REFRESH_TOKEN_NAME'],
            value=serializer.validated_data['refresh'],
            httponly=True,
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        )

        response.set_cookie(
            settings.AUTH_TOKEN_NAMES['GSI_TOKEN_NAME'],
            value=serializer.validated_data['gsi_token'],
            httponly=False,
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Overrided post method from TokenRefreshView
    Added cookie management
    """
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get(settings.AUTH_TOKEN_NAMES['REFRESH_TOKEN_NAME'])
        except TokenError as e:
            raise InvalidToken(e.args[0])

        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raw_response = Response(status.HTTP_401_UNAUTHORIZED)
            response = clean_cookies(raw_response)

            return response
        
        response = Response(status.HTTP_200_OK)

        response.set_cookie(
            settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME'],
            value=serializer.validated_data['access'],
            httponly=True,
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        )

        return response
    

class CookieTokenVerifyView(TokenVerifyView):
    """
    Overrided post method from TokenVerifyView
    Added cookie management
    """
    def post(self, request):
        try:
            access_token = request.COOKIES.get(settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME'])
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        serializer = self.get_serializer(data={'token': access_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return Response(status=status.HTTP_200_OK)
    

class CookieTokenLogoutView(APIView):
    """
    Used to remove cookies on logout
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_response = Response(status.HTTP_200_OK)
        response = clean_cookies(raw_response)

        return response