class CookieTokenStrategy:
    """
    Overrided djoser.social.token.jwt.TokenStrategy class
    only changed user value to gsi_token
    """
    
    @classmethod
    def obtain(cls, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user.gsi_token,
        }