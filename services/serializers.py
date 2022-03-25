from rest_framework import serializers

from items.serializers import AlterItemSerializer
from services.models import Invoice, Purchase, Rent


class PurchaseSerializer(serializers.ModelSerializer):
    item = AlterItemSerializer()

    class Meta:
        model = Purchase
        fields = [
            'id',
            'item',
            'invoice',
            'quantity',
            'path_template',
        ]


class AlterPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = ['item', 'quantity']

    def validate_quantity(self, value):
        """Проверка количество больше нуля"""
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than zero')
        return value


class RentSerializer(serializers.ModelSerializer):
    item = AlterItemSerializer()

    class Meta:
        model = Rent
        fields = [
            'id',
            'item',
            'invoice',
            'quantity',
            'path_template',
            'date_from',
            'date_to',
            'daily_payment',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    purchase_set = PurchaseSerializer(many=True, required=False, read_only=True)
    rent_set = RentSerializer(many=True, required=False, read_only=True)
    status = serializers.ChoiceField(Invoice.InvoiceStatuses.choices)
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'user_id',
            'status',
            'date_created',
            'status_updated',
            'price_total',
            'final_price',
            'purchase_set',
            'rent_set',
        ]

    def get_final_price(self, obj: Invoice) -> int:
        """Return final price with discount
        :param obj: Invoice
        :return: int
        """
        return obj.get_final_price_and_currency()[0]
