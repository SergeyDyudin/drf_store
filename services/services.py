import logging
from smtplib import SMTPDataError

from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from items.models import Item
from services.models import Invoice, Purchase

logger = logging.getLogger(__name__)


def pay_the_cart(request, invoice: Invoice):
    """Оплата заказа в корзине"""
    invoice.status = Invoice.InvoiceStatuses.PAID.value
    invoice.status_updated = timezone.now()

    final_price, new_currency = invoice.get_final_price_and_currency()
    invoice.user_profile.currency = new_currency

    invoice.user_profile.save()
    invoice.save()

    logger.info(f'Invoice {invoice} paid.')
    sent_email_payment_done(request, invoice)


@transaction.atomic
def create_purchase(request, item: Item, quantity: int) -> None:
    """Создание сервиса покупки для товара (добавление в корзину)"""
    if item.count_available >= quantity:
        invoice, created = Invoice.objects.get_or_create(
            user_id=CustomUser.objects.get(pk=request.user.id),
            status=Invoice.InvoiceStatuses.UNPAID.value
        )
        Purchase(item=item, invoice=invoice, quantity=quantity).save()
        item.count_available -= quantity
        item.save()

        try:
            sent_email_add_item_to_cart(request, {'item': item})
        except SMTPDataError:
            logger.error('Сообщение не было отправлено', exc_info=True)
    else:
        raise ValueError(_('Неверное количество товара'))


def sent_email_payment_done(request, invoice):
    """Отправка email пользователю об успешной оплате"""
    current_site = get_current_site(request)
    subject = 'Payment is done!'
    message = render_to_string('services/email_payment_done.html', {
        'user': request.user,
        'invoice': invoice,
        'current_site': current_site,
    })

    try:
        request.user.email_user(subject, message)
    except SMTPDataError:
        logger.error('Сообщение не было отправлено', exc_info=True)


def sent_email_add_item_to_cart(request, data):
    """Отправка email пользователю о добавлении товара в корзину"""
    subject = _(f'Add {data["item"]} to cart')
    current_site = get_current_site(request)
    message = render_to_string('services/email_add_to_cart.html', {
        'user': request.user,
        'data': data,
        'current_site': current_site,
        'cart_link': request.build_absolute_uri(reverse('services:cart'))
    })

    try:
        request.user.email_user(subject, message)
    except SMTPDataError:
        logger.error('Сообщение не было отправлено', exc_info=True)
