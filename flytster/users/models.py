from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils.timezone import now

from authentication.models import AuthToken, InvalidTokenError, EmailToken, PasswordToken

from .utils import new_user_email, verify_email, password_reset_email


class FlytsterUserManager(BaseUserManager):

    def create_user(self, first_name, last_name, email, password):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email)
        user.set_password(password)
        user.save(using=self._db)
        user.send_registration_email(user.email)

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


class FlytsterUser(AbstractBaseUser):

    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    recieve_notifications = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = FlytsterUserManager()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    @property
    def is_staff(self):
        return self.is_active and self.is_admin

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

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

    def send_email(self, subject, text, html=None, email=None):
        recipients = [email] if email else [self.email]
        try:
            send_mail(
                subject, text, settings.SERVER_EMAIL, recipients,
                fail_silently=False, html_message=html)
        except:
            print("SEND EMAIL ERROR")

    def send_registration_email(self, email):
        email_token = EmailToken(user=self, email=email)
        email_token.save()

        url = 'http://192.168.99.100:8000/api/v1/user/verify-email/{}'.format(email_token.token)

        context = {
            'full_name': self.get_full_name(),
            'verification_link': url
        }

        subject, text, html = new_user_email(context)
        self.send_email(subject, text, html=html)

    def send_verification_email(self, email):
        if hasattr(self, 'email_token') and self.email_token.id is not None:
            self.email_token.delete()

        if self.email == email and self.is_verified:
            return

        email_token = EmailToken(user=self, email=email)
        email_token.save()

        url = 'http://192.168.99.100:8000/api/v1/user/verify-email/{}'.format(email_token.token)

        context = {
            'full_name': self.get_full_name(),
            'verification_link': url
        }

        subject, text, html = verify_email(context)
        self.send_email(subject, text, html=html, email=email)

    def verify_email_token(self, token):
        try:
            email_token = EmailToken.objects.get(user=self)
        except EmailToken.DoesNotExist:
            raise InvalidTokenError('The verification token is invalid.')
        if email_token.is_expired:
            raise InvalidTokenError('The verification token has expired.')

        if email_token.token == token:
            self.email = email_token.email
            self.is_verified = True
            self.save()
            email_token.delete()
        else:
            raise InvalidTokenError('The verification token was invalid.')

    def request_password_reset(self):
        if hasattr(self, 'password_token') and self.password_token.id is not None:
            self.password_token.delete()

        password_token = PasswordToken(user=self)
        password_token.save()

        url = 'http://192.168.99.100:8000/api/v1/user/reset-password/{}'.format(password_token.token)

        context = {
            'full_name': self.get_full_name(),
            'verification_link': url
        }

        subject, text, html = password_reset_email(context)
        self.send_email(subject, text, html=html)
