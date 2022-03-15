import re

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


def validate_phone(value):
    regexp = r'^\+?\d{11,15}$'
    if not re.fullmatch(regexp, value):
        raise serializers.ValidationError(_('Invalid phone number'))
