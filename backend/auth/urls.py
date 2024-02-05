from django.urls import path, re_path, include
from .views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenVerifyView,
    CookieTokenLogoutView,
    CookieProviderAuthView,
)


urlpatterns = [
    path('', include('djoser.urls')),

    # social auth urls, only Google oauth 2.0 
    re_path(r"^o/(?P<provider>\S+)/$", CookieProviderAuthView.as_view()),

    path('jwt/create/', CookieTokenObtainPairView.as_view()),
    path('jwt/refresh/', CookieTokenRefreshView.as_view()),
    path('jwt/verify/', CookieTokenVerifyView.as_view()),
    path('jwt/logout/', CookieTokenLogoutView.as_view()),
]