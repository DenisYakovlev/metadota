from django.conf import settings
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Modified JWTAuthentication.
    Instead of looking for token from Authorization header
    looks for it in cookies
    """
    def authenticate(self, request):
        cookie = request.COOKIES.get(settings.AUTH_TOKEN_NAMES['ACCESS_TOKEN_NAME'])
        if cookie is None:
            return None
        
        raw_token = cookie.encode(HTTP_HEADER_ENCODING)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
