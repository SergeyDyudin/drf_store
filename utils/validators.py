import re

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def validate_phone(value):
    regexp = r'^\+?\d{11,15}$'
    if not re.fullmatch(regexp, value):
        raise serializers.ValidationError(_('Invalid phone number'))
