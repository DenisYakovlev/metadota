from rest_framework import serializers
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserList(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'gsi_token', 'is_staff', 'date_joined']