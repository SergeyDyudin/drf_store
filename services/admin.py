from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _, ngettext

from .filters import UnpaidOldInvoiceListFilter
from .models import Purchase, Rent, Invoice


class PurchaseInlineAdmin(admin.StackedInline):
    model = Purchase
    extra = 0
    autocomplete_fields = [
        'item',
    ]
    verbose_name = _('purchase')
    verbose_name_plural = _('purchases')
    readonly_fields = [
        'price'
    ]

    @admin.display(description=_('Price'))
    def price(self, obj):
        return obj.price


class RentInlineAdmin(admin.StackedInline):
    model = Rent
    extra = 0
    autocomplete_fields = [
        'item',
    ]
    verbose_name = _('rent')
    verbose_name_plural = _('rents')
    readonly_fields = [
        'price'
    ]

    @admin.display(description=_('Price'))
    def price(self, obj):
        return obj.price


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'status',
        'price_total'
    ]
    list_filter = [
        'status',
        UnpaidOldInvoiceListFilter
    ]
    readonly_fields = [
        'date_created',
        'price_total'
    ]
    autocomplete_fields = [
        'user_id'
    ]
    inlines = [
        PurchaseInlineAdmin,
        RentInlineAdmin
    ]
    search_fields = [
        'id',
        'user_id__email',
    ]
    actions = [
        'make_canceled',
    ]

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'status':
            if not request.user.has_perm('can_change_status'):
                choices = db_field.get_choices()
                choices.remove((1, _('Оплачен')))
                choices.remove(('', '---------'))
                kwargs['choices'] = choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    @admin.action(description=_('Mark invoice status as CANCELED'))
    def make_canceled(self, request, queryset):
        updated = queryset.update(status=Invoice.InvoiceStatuses.CANCELED.value)
        self.message_user(
            request,
            ngettext(
                _('%d invoice was successfully marked as canceled.'),
                _('%d invoices were successfully marked as canceled.'),
                updated,
            ) % updated, messages.SUCCESS
        )


class PurchaseAdmin(admin.ModelAdmin):
    readonly_fields = [
        'price'
    ]
    autocomplete_fields = [
        'item',
        'invoice',
    ]
    list_display = [
        'item',
        'status_invoice',
        'quantity',
    ]
    search_fields = [
        'item__title'
    ]
    search_help_text = 'Enter item'

    @admin.display(description=_('Status'))
    def status_invoice(self, obj):
        return obj.invoice.status

    @admin.display(description=_('Price'))
    def price(self, obj):
        return obj.price


class RentAdmin(admin.ModelAdmin):
    readonly_fields = [
        'price'
    ]
    autocomplete_fields = [
        'item',
        'invoice',
    ]
    list_display = [
        'item',
        'status_invoice',
        'quantity',
    ]
    search_fields = [
        'item__title'
    ]
    search_help_text = 'Enter item'

    @admin.display(description=_('Status'))
    def status_invoice(self, obj):
        return obj.invoice.status

    @admin.display(description=_('Price'))
    def price(self, obj):
        return obj.price


admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Rent, RentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
