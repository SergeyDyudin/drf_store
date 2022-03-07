from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from services.models import Invoice


class UnpaidOldInvoiceListFilter(admin.SimpleListFilter):
    title = _('unpaid invoices by')

    parameter_name = 'unpaid-invoices'

    def lookups(self, request, model_admin):
        return (
            ('week', _('Last week')),
            ('month', _('Last month')),
            ('year', _('Last year')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'week':
            return queryset.filter(status=Invoice.InvoiceStatuses.UNPAID.value).filter(
                date_created__gte=timezone.now()-timezone.timedelta(weeks=1)
            )
        if self.value() == 'month':
            return queryset.filter(status=Invoice.InvoiceStatuses.UNPAID.value).filter(
                date_created__gte=timezone.now()-timezone.timedelta(weeks=4)
            )
        if self.value() == 'year':
            return queryset.filter(status=Invoice.InvoiceStatuses.UNPAID.value).filter(
                date_created__gte=timezone.now()-timezone.timedelta(days=365)
            )
