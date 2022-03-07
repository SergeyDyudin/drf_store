import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone(value):
    regexp = r'^\+?\d{11,15}$'
    if not re.fullmatch(regexp, value):
        raise ValidationError(message=_('Invalid phone number'), code='invalid')
