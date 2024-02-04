from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class GSITokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Overrided validate method from TokenObtainPairSerializer
    gsi_token is stored in cookies in view
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['gsi_token'] = self.user.gsi_token

        return data