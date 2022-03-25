import datetime
import logging
from smtplib import SMTPDataError

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import get_object_or_404

from accounts.models import CustomUser
from items.models import Item
from services.models import Invoice, Purchase, Rent

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
def create_purchase(request, data: dict) -> None:
    """Создание сервиса покупки для товара (добавление в корзину)"""
    item = get_object_or_404(Item, pk=data['item'])
    quantity = int(data['quantity'])

    if item.count_available >= quantity:
        invoice, created = Invoice.objects.get_or_create(
            user_id=CustomUser.objects.get(pk=request.user.id),
            status=Invoice.InvoiceStatuses.UNPAID.value
        )
        Purchase(item=item, invoice=invoice, quantity=quantity).save()
        item.count_available -= quantity
        item.save()

        try:
            data['item'] = item
            sent_email_add_item_to_cart(request, data)
        except SMTPDataError:
            logger.error('Сообщение не было отправлено', exc_info=True)
    else:
        raise ValueError(_('Неверное количество товара'))


@transaction.atomic
def create_rent(request, data: dict) -> None:
    """Создание сервиса аренды для товара (добавление в корзину)"""
    item = get_object_or_404(Item, pk=data['item'])

    if item.count_available >= 1:
        invoice, created = Invoice.objects.get_or_create(
            user_id=CustomUser.objects.get(pk=request.user.id),
            status=Invoice.InvoiceStatuses.UNPAID.value
        )
        Rent(item=item,
             invoice=invoice,
             quantity=1,
             date_from=data['date_from'],
             date_to=data['date_to'],
             daily_payment=item.price * settings.PERCENT_OF_PRICE).save()
        item.count_available -= 1
        item.save()

        try:
            data['item'] = item
            sent_email_add_item_to_cart(request, data)
        except SMTPDataError:
            logger.error('Сообщение не было отправлено', exc_info=True)
    else:
        raise ValueError(_('Товар отсутствует на складе'))


def get_data_for_rent(item_id: int) -> tuple[dict, dict]:
    """Return data for present at rent form"""
    data = {
        'item': item_id,
        'date_from': timezone.localdate(),
        'date_to': timezone.localdate() + datetime.timedelta(days=1),
    }

    item = get_object_or_404(Item, pk=item_id)
    daily_payment = item.price * settings.PERCENT_OF_PRICE

    return data, {'daily_payment': daily_payment}


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
