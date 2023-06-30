from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email or not username or not password:
            raise ValueError('The given values are not valid')
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, email, password, **extra_fields)
    

class User(AbstractUser):
    username = models.CharField(max_length=32, blank=False, null=False, unique=True)
    gsi_token = models.UUIDField(default=uuid.uuid4, editable=False,unique=True)
    
    USERNAME_FIELD = 'username'
    
    objects = UserManager()
    