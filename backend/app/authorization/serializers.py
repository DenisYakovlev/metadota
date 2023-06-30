from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from user.models import User

class RegistrationSerializer(ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password', 'gsi_token']
    
    def validate(self, data):
        """
        Checks to be sure that the received password and confirm_password
        fields are exactly the same
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
        
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])