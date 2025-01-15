from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import CustomUserManager
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    username = None
    full_name = models.CharField(_('full name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    personal_number = models.CharField(_('personal number'), max_length=20)
    is_librarian = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=True if settings.DEBUG else False, verbose_name=_("Is Authorized"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['full_name', 'personal_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
