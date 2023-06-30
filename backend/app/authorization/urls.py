from django.urls import path 
from .views import SignIn, SignUp

urlpatterns = [
    path('signin', SignIn.as_view()),
    path('signup', SignUp),
]
