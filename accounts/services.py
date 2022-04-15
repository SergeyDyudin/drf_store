import logging

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.tokens import account_activation_token

logger = logging.getLogger(__name__)


def send_activation_email(request, user):
    current_site = get_current_site(request)
    subject = f'Activate Your {current_site} Account'
    message = render_to_string('accounts/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)
    logger.info(f'Sent activation email to {user.email}')