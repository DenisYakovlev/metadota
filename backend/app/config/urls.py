from django.urls import path 
from .views import SendDotaGSIFile, SendCSGOGSIFile, SendImage

urlpatterns = [
    path('gsi_dota', SendDotaGSIFile),
    path('gsi_csgo', SendCSGOGSIFile),
    path("<str:path>", SendImage)
]