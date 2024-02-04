from django.urls import path, include
from .views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenVerifyView,
    CookieTokenLogoutView
)


urlpatterns = [
    path('', include('djoser.urls')),
    path('jwt/create/', CookieTokenObtainPairView.as_view()),
    path('jwt/refresh/', CookieTokenRefreshView.as_view()),
    path('jwt/verify/', CookieTokenVerifyView.as_view()),
    path('jwt/logout/', CookieTokenLogoutView.as_view()),
]