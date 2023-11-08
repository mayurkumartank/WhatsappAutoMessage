import re
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


def validate_digit_phone_number(value):
    if not re.match(r'^\d+$', value):
        raise ValidationError('Phone number must contain only digits.')
    if  len(value) != 10:
        raise ValidationError('Phone number must have at least 10 digits.')
    

class MessageModel(models.Model):
    user_name = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="user")
    phone_number =  models.CharField(max_length=10,validators=[validate_digit_phone_number])
    meessage = models.TextField(null=True,blank=True)
    message_file = models.FileField(upload_to='uploads/message_file/',null=True,blank=True)


