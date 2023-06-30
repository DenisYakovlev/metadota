from django.urls import path
from .views import ProcessDotaGame, ProcessCSGOGame

urlpatterns = [
    path("dota", ProcessDotaGame),
    path("csgo", ProcessCSGOGame)
]
