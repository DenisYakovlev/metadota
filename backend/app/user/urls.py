from django.urls import path
from .views import UserInfo

urlpatterns = [
    path('me', UserInfo),
]