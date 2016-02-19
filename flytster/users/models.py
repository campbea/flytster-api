from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now

from authentication.models import AuthToken


class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, email, password):
        user = self.model(
            first_name=first_name,
            last_name=last_name, 
            email=email)
        user.set_password(password)
        user.save(using=self._db)

        AuthToken.objects.create(user=user)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    # Required By Django
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    @property
    def is_staff(self):
        return self.is_active and self.is_admin

    def get_full_name(self):
        return self.first_name + self.last_name

    def get_short_name(self):
        return self.first_name

    def str(self):
        return self.email

    def login(self):
        for token in self.auth_tokens.all():
            token.is_expired

        AuthToken.objects.create(user=self)
        self.last_login = now()
        self.save()
