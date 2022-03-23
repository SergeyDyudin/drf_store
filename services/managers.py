from django.db import models
from django.db.models import Sum, F, Count, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractDay


class InvoiceManager(models.Manager):

    def get_queryset(self):
        qs = super(InvoiceManager, self).get_queryset().\
            select_related('user_id').prefetch_related('rent_set', 'purchase_set')
        return qs


class ServiceManager(models.Manager):

    def get_queryset(self):
        qs = super(ServiceManager, self).get_queryset().select_related('invoice', 'item')
        return qs.annotate(price=F('item__price') * F('quantity'))


class RentManager(models.Manager):

    def get_queryset(self):
        qs = super(RentManager, self).get_queryset().select_related('invoice', 'item')
        return qs.annotate(
            price=F('quantity') * F('daily_payment') * (
                ExtractDay(ExpressionWrapper(F('date_to') - F('date_from'), output_field=DurationField())) + 1
            )
        )
