from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from djoser.social.views import ProviderAuthView


access = settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME']
refresh = settings.AUTH_TOKEN_NAMES['REFRESH_TOKEN_NAME']
gsi = settings.AUTH_TOKEN_NAMES['GSI_TOKEN_NAME']

access_lifetime = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
gsi_lifetime = refresh_lifetime = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())


def clean_cookies(response):
    """
    Just clean token cookies from response object
    """
    response.delete_cookie(refresh)
    response.delete_cookie(access)
    response.delete_cookie(gsi)

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
            access,
            value=serializer.validated_data['access'],
            httponly=True,
            max_age=access_lifetime,
        )

        response.set_cookie(
            refresh,
            value=serializer.validated_data['refresh'],
            httponly=True,
            max_age=refresh_lifetime,
        )

        response.set_cookie(
            gsi,
            value=serializer.validated_data['gsi_token'],
            httponly=False,
            max_age=gsi_lifetime
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Overrided post method from TokenRefreshView
    Added cookie management
    """
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get(refresh)
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
            access,
            value=serializer.validated_data['access'],
            httponly=True,
            max_age=access_lifetime,
        )

        return response
    

class CookieTokenVerifyView(TokenVerifyView):
    """
    Overrided post method from TokenVerifyView
    Added cookie management
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            access_token = request.COOKIES.get(access)
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
    Use to remove cookies on logout
    """
    permission_classes = [AllowAny]

    def post(self, request):
        raw_response = Response(status.HTTP_200_OK)
        response = clean_cookies(raw_response)

        return response
    

class CookieProviderAuthView(ProviderAuthView):
    """
    Overrided post method from ProviderAuthView. Added cookies to response object.
    gsi_token is stored as user value in raw_response data because of ProviderAuthSerializer fields.
    Needed to override serializer class just to rename 'user' to 'gsi_token' so this is forbidden 
    """
    def post(self, request, *args, **kwargs):
        raw_response = super().post(request, *args, **kwargs)
        response = Response(status.HTTP_200_OK, headers=raw_response.headers)

        response.set_cookie(
            access,
            value=raw_response.data['access'],
            httponly=True,
            max_age=access_lifetime,
        )

        response.set_cookie(
            refresh,
            value=raw_response.data['refresh'],
            httponly=True,
            max_age=refresh_lifetime,
        )

        response.set_cookie(
            gsi,
            value=raw_response.data['user'],
            httponly=False,
            max_age=gsi_lifetime
        )

        return response