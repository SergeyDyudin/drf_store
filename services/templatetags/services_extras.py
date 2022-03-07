from django import template

from services.models import Invoice

register = template.Library()


@register.simple_tag(name='count_items')
def count_items_in_invoice(user):
    try:
        invoice = Invoice.objects.get(user_id=user.id, status=Invoice.InvoiceStatuses.UNPAID.value)
        return invoice.purchase_set.count() + invoice.rent_set.count()
    except Invoice.DoesNotExist:
        return 0
