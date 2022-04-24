import csv
import logging
from smtplib import SMTPDataError

from django.contrib import admin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.managers import CustomUserManager
from utils.validators import validate_phone

logger = logging.getLogger(__name__)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = ASCIIUsernameValidator()

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True, max_length=50)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_absolute_url(self):
        return reverse('accounts:account', kwargs={'pk': self.pk})


class Region(models.Model):
    region = models.CharField(_('Регион'), max_length=50)
    country = models.CharField(_('Страна'), max_length=50)

    class Meta:
        unique_together = ['region', 'country']
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        ordering = ('region',)

    def __str__(self):
        return f'{self.region}, {self.country}'

    @staticmethod
    def import_from_csv(file_name: str):
        """
        Import regions from csv to database
        :param file_name:
        :return:
        """
        with open(file_name) as file:
            reader = csv.reader(file)
            return Region.objects.bulk_create(
                [Region(region=row[2], country='Россия') for row in reader][1:],
                ignore_conflicts=True
            )


class Profile(models.Model):
    user = models.OneToOneField(to=CustomUser, related_name='profile', on_delete=models.CASCADE)
    phone = models.CharField(_('Phone'), max_length=20, validators=[validate_phone], blank=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    region = models.ForeignKey(to=Region, blank=True, null=True, on_delete=models.SET_NULL)
    currency = models.PositiveIntegerField(_('Virtual currency'), default=0, blank=True)
    email_confirmed = models.BooleanField(_('Email confirmed'), default=False)

    @property
    def age(self):
        today = timezone.now()
        if self.birthday is not None:
            return today.year - self.birthday.year - \
                   ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    @property
    @admin.display(description=_('Full name'))
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return self.user.email

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            old_currency = Profile.objects.get(pk=self.pk).currency
            if old_currency != self.currency:
                try:
                    self.user.email_user(subject='Change values',
                                         message=f'Currency = {self.currency}')
                except SMTPDataError:
                    logger.error('Сообщение не было отправлено', exc_info=True)
        except Profile.DoesNotExist:
            pass
        super(Profile, self).save()

    def is_adult(self):
        if self.age:
            return True if self.age >= 18 else False
        return False
